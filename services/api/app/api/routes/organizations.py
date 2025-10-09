from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db_session,
    require_org_admin_or_superuser,
    require_superuser,
    require_user,
)
from app.core.config import settings
from app.models.organization import OrgMembership, Organization, UserProfile
from app.models.user import User
from app.schemas.organization import (
    EnrollTokenCreateIn,
    EnrollTokenCreateOut,
    OrgMemberListResponse,
    OrgMemberOut,
    OrganizationCreate,
    OrganizationEnrollIn,
    OrganizationOut,
    OrganizationUpdate,
)
from app.services.enrollment_service import EnrollmentService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=List[OrganizationOut])
def list_organizations(
    search: str | None = Query(default=None, min_length=1, max_length=255),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db_session),
) -> List[OrganizationOut]:
    stmt = select(Organization).order_by(Organization.name.asc()).limit(limit)

    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Organization.slug.ilike(like), Organization.name.ilike(like)))

    if current_user.role != "superuser":
        if current_user.organization_id:
            stmt = stmt.where(Organization.id == current_user.organization_id)
        else:
            return []

    return db.scalars(stmt).all()


@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    data: OrganizationCreate,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> OrganizationOut:
    slug = data.slug.strip().lower()
    existing = (
        db.query(Organization)
        .filter(Organization.slug == slug)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization slug already exists.")

    organization = Organization(
        name=data.name.strip(),
        slug=slug,
        type=data.type.strip().lower() if data.type else None,
        logo_url=data.logo_url.strip() if data.logo_url else None,
        status="active",
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


@router.patch("/{organization_id}", response_model=OrganizationOut)
def update_organization(
    organization_id: int,
    data: OrganizationUpdate,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> OrganizationOut:
    organization = db.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")

    if data.status and organization.status != data.status:
        organization.status = data.status
    if data.name and organization.name != data.name.strip():
        organization.name = data.name.strip()
    if data.type is not None:
        organization.type = data.type.strip().lower() if data.type else None
    if data.logo_url is not None:
        organization.logo_url = data.logo_url.strip() or None

    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


@router.get("/{organization_id}/members", response_model=OrgMemberListResponse)
def list_organization_members(
    organization_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_org_admin_or_superuser),
    db: Session = Depends(get_db_session),
) -> OrgMemberListResponse:
    organization = db.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    if organization.status != "active" and current_user.role != "superuser":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization is disabled.")

    if current_user.role != "superuser":
        membership = (
            db.query(OrgMembership)
            .filter(
                OrgMembership.organization_id == organization_id,
                OrgMembership.user_id == current_user.id,
            )
            .first()
        )
        if membership is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    stmt = (
        select(
            User.id,
            User.username,
            User.email,
            User.role,
            User.account_type,
            OrgMembership.org_role,
            OrgMembership.status,
        )
        .join(OrgMembership, OrgMembership.user_id == User.id)
        .where(OrgMembership.organization_id == organization_id)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).all()

    members = [
        OrgMemberOut(
            user_id=row.id,
            username=row.username,
            email=row.email,
            role=row.role,
            account_type=row.account_type,
            org_role=row.org_role,
            status=row.status,
        )
        for row in rows
    ]

    total_stmt = (
        select(func.count())
        .select_from(OrgMembership)
        .where(OrgMembership.organization_id == organization_id)
    )
    total = int(db.scalar(total_stmt) or 0)

    return OrgMemberListResponse(items=members, total=total)


@router.post("/{organization_id}/enroll-tokens", response_model=EnrollTokenCreateOut)
def create_enroll_token(
    organization_id: int,
    data: EnrollTokenCreateIn,
    current_user: User = Depends(require_org_admin_or_superuser),
    db: Session = Depends(get_db_session),
) -> EnrollTokenCreateOut:
    organization = db.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    if organization.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization is disabled.")

    if current_user.role != "superuser":
        membership = (
            db.query(OrgMembership)
            .filter(
                OrgMembership.organization_id == organization_id,
                OrgMembership.user_id == current_user.id,
                OrgMembership.org_role == "org_admin",
            )
            .first()
        )
        if membership is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    service = EnrollmentService(db)
    token, entity = service.create_enroll_token(
        organization_id=organization_id,
        expires_in_minutes=data.expires_in_minutes,
    )
    join_url = f"{settings.enrollment_join_base}{token}"

    profile = current_user.profile
    if profile is None:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.flush()
    profile.qr_code_uri = join_url

    db.commit()
    return EnrollTokenCreateOut(token=token, expires_at=entity.expires_at, enroll_url=join_url)


@router.post("/enroll", response_model=OrganizationOut)
def enroll_current_user(
    data: OrganizationEnrollIn,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db_session),
) -> OrganizationOut:
    service = EnrollmentService(db)
    try:
        organization = service.consume_token(data.token.strip(), current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    notification_service = NotificationService(db)
    notification_service.create(
        user_id=current_user.id,
        type="organization_enroll",
        title="Organization enrollment successful",
        body=f"You are now part of {organization.name}.",
    )

    db.commit()
    db.refresh(organization)
    return organization
