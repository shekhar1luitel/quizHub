import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("httpx")

from sqlalchemy import select

from app.core.security import get_password_hash  # noqa: E402
from app.models.organization import Notification, OrgMembership  # noqa: E402
from app.models.user import User  # noqa: E402

from .test_auth import TestingSessionLocal, client  # noqa: E402


SUPER_EMAIL = "root@example.com"
SUPER_PASSWORD = "superpass123"


def _ensure_superuser() -> None:
    session = TestingSessionLocal()
    try:
        existing = session.execute(
            select(User).where(User.email == SUPER_EMAIL)
        ).scalar_one_or_none()
        if existing:
            return
        user = User(
            email=SUPER_EMAIL,
            username="rootadmin",
            hashed_password=get_password_hash(SUPER_PASSWORD),
            role="superuser",
            status="active",
            account_type="staff",
        )
        session.add(user)
        session.commit()
    finally:
        session.close()


def _auth_headers() -> dict[str, str]:
    _ensure_superuser()
    response = client.post(
        "/api/auth/login",
        json={"email": SUPER_EMAIL, "password": SUPER_PASSWORD},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_user_management_and_enrollment_flow():
    headers = _auth_headers()

    # dispatch should fail without config
    resp = client.post("/api/admin/email/dispatch", headers=headers)
    assert resp.status_code == 400

    # configure mail settings
    resp = client.put(
        "/api/admin/config/mail",
        json={
            "host": "smtp.example.com",
            "port": 2525,
            "username": None,
            "password": None,
            "tls_ssl": False,
            "from_name": "Quiz Ops",
            "from_email": "ops@example.com",
        },
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_configured"] is True

    # now dispatch (no events queued yet)
    resp = client.post("/api/admin/email/dispatch", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["processed"] == 0

    # create organization
    resp = client.post(
        "/api/organizations",
        json={"name": "Test Academy", "slug": "test-academy", "type": "education"},
        headers=headers,
    )
    assert resp.status_code == 201
    organization = resp.json()
    org_id = organization["id"]

    # create organization admin without queuing email
    resp = client.post(
        "/api/admin/users",
        json={
            "username": "orgadmin",
            "email": "orgadmin@example.com",
            "password": "password123",
            "role": "org_admin",
            "organization_id": org_id,
            "send_invite_email": False,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    admin_user = resp.json()
    assert admin_user["account_type"] == "organization_admin"

    # verify notification queued for admin user
    session = TestingSessionLocal()
    try:
        notifications = session.execute(
            select(Notification).where(Notification.user_id == admin_user["id"])
        ).scalars().all()
        assert len(notifications) == 1
    finally:
        session.close()

    # generate enrollment token
    resp = client.post(
        f"/api/organizations/{org_id}/enroll-tokens",
        json={"expires_in_minutes": 60},
        headers=headers,
    )
    assert resp.status_code == 200
    enroll_token = resp.json()["token"]

    # register learner with enrollment token
    resp = client.post(
        "/api/auth/register",
        json={
            "username": "student1",
            "email": "student1@example.com",
            "password": "password123",
            "enroll_token": enroll_token,
        },
    )
    assert resp.status_code == 201
    learner = resp.json()
    assert learner["account_type"] == "organization_member"
    learner_id = learner["id"]

    # confirm membership stored
    session = TestingSessionLocal()
    try:
        membership = session.execute(
            select(OrgMembership).where(
                OrgMembership.organization_id == org_id,
                OrgMembership.user_id == learner_id,
            )
        ).scalar_one_or_none()
        assert membership is not None
    finally:
        session.close()

    # broadcast notification to organization
    resp = client.post(
        "/api/admin/notifications",
        json={
            "type": "update",
            "title": "Welcome",
            "body": "You have joined Test Academy",
            "organization_id": org_id,
        },
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["notified_users"] >= 1

    # list organization members
    resp = client.get(f"/api/organizations/{org_id}/members", headers=headers)
    assert resp.status_code == 200
    member_list = resp.json()
    assert member_list["total"] >= 2
