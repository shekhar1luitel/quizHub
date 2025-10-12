import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("httpx")

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient  # noqa: E402

from app.api.deps import get_db_session
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import PlatformUser, User


engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_session] = override_get_db

client = TestClient(app)


def test_register_and_login_flow():
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "QuizFan",
            "email": "User@example.com",
            "password": "password123",
        },
    )
    assert register_response.status_code == 201
    data = register_response.json()
    assert data["email"] == "user@example.com"
    assert data["role"] == "user"
    assert data["account_type"] == "individual"
    assert "id" in data

    login_response = client.post(
        "/api/auth/login",
        json={"email": "USER@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert token_data["token_type"] == "bearer"
    assert token_data["access_token"]


def test_update_user_profile_and_password():
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "settings_user",
            "email": "settings@example.com",
            "password": "initialPass123",
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    db = TestingSessionLocal()
    try:
        user = db.get(User, user_id)
        user.status = "active"
        db.commit()
    finally:
        db.close()

    login_response = client.post(
        "/api/auth/login",
        json={"email": "settings@example.com", "password": "initialPass123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_response = client.get("/api/users/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["username"] == "settings_user"
    assert me_data["profile"] is None
    assert "memberships" in me_data
    assert me_data["memberships"] == []
    assert me_data["platform_account"] is None
    assert me_data["organization_account"] is None
    assert me_data["learner_account"] is not None
    if me_data["organization"] is not None:
        assert "type" in me_data["organization"]

    update_response = client.patch(
        "/api/users/me",
        headers=headers,
        json={
            "username": "updated_user",
            "name": "Quiz Master",
            "phone": "555-0112",
        },
    )
    assert update_response.status_code == 200
    payload = update_response.json()
    assert payload["username"] == "updated_user"
    assert payload["profile"]["name"] == "Quiz Master"
    assert payload["profile"]["phone"] == "555-0112"
    assert payload["memberships"] == []
    assert "avatar_url" in payload["profile"]
    assert payload["learner_account"] is not None
    assert payload["platform_account"] is None

    password_response = client.patch(
        "/api/users/me",
        headers=headers,
        json={
            "current_password": "initialPass123",
            "new_password": "NewSecret456",
        },
    )
    assert password_response.status_code == 200

    relogin_response = client.post(
        "/api/auth/login",
        json={"email": "settings@example.com", "password": "NewSecret456"},
    )
    assert relogin_response.status_code == 200


def test_admin_cannot_access_learner_endpoints():
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "admin_blocked",
            "email": "admin_blocked@example.com",
            "password": "AdminPass123",
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    db = TestingSessionLocal()
    try:
        user = db.get(User, user_id)
        user.status = "active"
        user.role = "admin"
        user.account_type = "staff"
        if db.execute(select(PlatformUser).where(PlatformUser.user_id == user.id)).scalar_one_or_none() is None:
            db.add(PlatformUser(user_id=user.id))
        db.commit()
    finally:
        db.close()

    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin_blocked@example.com", "password": "AdminPass123"},
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    dashboard_response = client.get("/api/dashboard/summary", headers=headers)
    assert dashboard_response.status_code == 403

    analytics_response = client.get("/api/analytics/overview", headers=headers)
    assert analytics_response.status_code == 403
