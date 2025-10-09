from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin, require_superuser
from app.core.security import get_password_hash
from app.models.category import Category
from app.models.organization import OrgMembership, Organization
from app.models.question import Question, QuizQuestion
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.admin import AdminCategorySnapshot, AdminOverview, AdminRecentQuiz, AdminTotals
from app.schemas.management import (
    AdminNotificationCreate,
    AdminNotificationResult,
    AdminUserCreate,
    AdminUserListResponse,
    AdminUserOut,
    AdminUserStatusUpdate,
    EmailDispatchResult,
    MailConfigIn,
    MailConfigOut,
)
from app.services.config_service import ConfigService
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=AdminOverview)
def get_admin_overview(
    _: None = Depends(require_admin),
    db: Session = Depends(get_db_session),
) -> AdminOverview:
    totals = AdminTotals(
        total_quizzes=int(db.scalar(select(func.count()).select_from(Quiz)) or 0),
        active_quizzes=int(
            db.scalar(select(func.count()).select_from(Quiz).where(Quiz.is_active.is_(True))) or 0
        ),
        total_questions=int(db.scalar(select(func.count()).select_from(Question)) or 0),
        inactive_questions=int(
            db.scalar(select(func.count()).select_from(Question).where(Question.is_active.is_(False))) or 0
        ),
        total_categories=int(db.scalar(select(func.count()).select_from(Category)) or 0),
        total_users=int(db.scalar(select(func.count()).select_from(User)) or 0),
    )

    recent_rows = db.execute(
        select(
            Quiz.id,
            Quiz.title,
            Quiz.is_active,
            Quiz.created_at,
            func.count(QuizQuestion.question_id).label("question_count"),
        )
        .join(QuizQuestion, QuizQuestion.quiz_id == Quiz.id, isouter=True)
        .group_by(Quiz.id)
        .order_by(Quiz.created_at.desc())
        .limit(8)
    ).all()

    recent_quizzes: List[AdminRecentQuiz] = [
        AdminRecentQuiz(
            id=row.id,
            title=row.title,
            question_count=int(row.question_count or 0),
            is_active=bool(row.is_active),
            created_at=row.created_at,
        )
        for row in recent_rows
    ]

    top_category_rows = db.execute(
        select(
            Category.id,
            Category.name,
            func.count(Question.id).label("question_count"),
        )
        .join(Question, Question.category_id == Category.id, isouter=True)
        .group_by(Category.id)
        .order_by(func.count(Question.id).desc(), Category.name.asc())
        .limit(6)
    ).all()

    top_categories = [
        AdminCategorySnapshot(
            id=row.id,
            name=row.name,
            question_count=int(row.question_count or 0),
        )
        for row in top_category_rows
    ]

    return AdminOverview(
        totals=totals,
        recent_quizzes=recent_quizzes,
        top_categories=top_categories,
    )


def _apply_user_filters(
    stmt,
    *,
    role: str | None,
    status_value: str | None,
    account_type: str | None,
    organization_id: int | None,
    search: str | None,
):
    if role:
        stmt = stmt.where(User.role == role)
    if status_value:
        stmt = stmt.where(User.status == status_value)
    if account_type:
        stmt = stmt.where(User.account_type == account_type)
    if organization_id:
        stmt = stmt.where(User.organization_id == organization_id)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                User.username.ilike(like),
                User.email.ilike(like),
            )
        )
    return stmt


@router.get("/users", response_model=AdminUserListResponse)
def list_admin_users(
    role: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    account_type: str | None = Query(default=None),
    organization_id: int | None = Query(default=None),
    search: str | None = Query(default=None, min_length=2, max_length=255),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> AdminUserListResponse:
    search_value = search.strip() if search else None

    base_stmt = select(User).order_by(User.created_at.desc())
    base_stmt = _apply_user_filters(
        base_stmt,
        role=role,
        status_value=status_value,
        account_type=account_type,
        organization_id=organization_id,
        search=search_value,
    ).limit(limit).offset(offset)
    users = db.scalars(base_stmt).all()

    count_stmt = select(func.count()).select_from(User)
    count_stmt = _apply_user_filters(
        count_stmt,
        role=role,
        status_value=status_value,
        account_type=account_type,
        organization_id=organization_id,
        search=search_value,
    )
    total = int(db.scalar(count_stmt) or 0)
    return AdminUserListResponse(items=users, total=total)


@router.post("/users", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    data: AdminUserCreate,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> AdminUserOut:
    username = data.username
    email = data.email.strip().lower()

    duplicate = (
        db.query(User)
        .filter(or_(User.username == username, User.email == email))
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists.",
        )

    organization_id = data.organization_id
    if data.role == "org_admin":
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="organization_id is required for org_admin role.",
            )
        organization = db.get(Organization, organization_id)
        if not organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    else:
        organization = None
        organization_id = None

    if data.role in {"admin", "superuser"}:
        account_type = "staff"
    elif data.role == "org_admin":
        account_type = "organization_admin"
    else:
        account_type = "individual"

    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        status="active",
        account_type=account_type,
        organization_id=organization_id,
    )
    db.add(user)
    db.flush()

    if organization:
        membership = (
            db.query(OrgMembership)
            .filter(
                OrgMembership.organization_id == organization.id,
                OrgMembership.user_id == user.id,
            )
            .first()
        )
        if membership is None:
            membership = OrgMembership(
                organization_id=organization.id,
                user_id=user.id,
                org_role="org_admin",
                status="active",
            )
            db.add(membership)
        else:
            membership.org_role = "org_admin"
            membership.status = "active"

    if data.send_notification:
        notification_service = NotificationService(db)
        notification_service.create(
            user_id=user.id,
            type="admin_access",
            title="Admin access granted",
            body="You have been granted admin privileges. Sign in to configure your workspace.",
        )

    if data.send_invite_email:
        email_service = EmailService(db)
        email_service.enqueue(
            to_email=user.email,
            template="admin_user_invite",
            payload={"username": user.username},
        )

    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/status", response_model=AdminUserOut)
def update_admin_user_status(
    user_id: int,
    payload: AdminUserStatusUpdate,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> AdminUserOut:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.status = payload.status
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/config/mail", response_model=MailConfigOut)
def get_mail_config(
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> MailConfigOut:
    service = ConfigService(db)
    return service.get_mail_config()


@router.put("/config/mail", response_model=MailConfigOut)
def update_mail_config(
    data: MailConfigIn,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> MailConfigOut:
    service = ConfigService(db)
    config = service.save_mail_config(data)
    db.commit()
    return config


@router.post("/email/dispatch", response_model=EmailDispatchResult)
def dispatch_email_events(
    limit: int = Query(default=20, ge=1, le=100),
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> EmailDispatchResult:
    service = EmailService(db)
    try:
        result = service.dispatch_pending(limit=limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.commit()
    return result


@router.post("/notifications", response_model=AdminNotificationResult)
def create_admin_notification(
    data: AdminNotificationCreate,
    _: None = Depends(require_superuser),
    db: Session = Depends(get_db_session),
) -> AdminNotificationResult:
    notification_service = NotificationService(db)

    target_ids: set[int] = set(data.user_ids or [])

    if data.organization_id:
        stmt = (
            select(User.id)
            .where(User.organization_id == data.organization_id)
            .where(User.status == "active")
        )
        org_user_ids = db.scalars(stmt).all()
        target_ids.update(org_user_ids)

    notified = notification_service.create_many(
        list(target_ids),
        type=data.type,
        title=data.title,
        body=data.body,
        meta=data.meta,
    )
    db.commit()
    return AdminNotificationResult(notified_users=notified)
