from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.core.config import settings
from app.models.organization import EmailEvent
from app.models.user import EmailVerificationToken, User
from app.schemas.auth import (
    LoginIn,
    ResendVerificationIn,
    Token,
    VerifyEmailIn,
)
from app.schemas.user import UserCreate, UserOut
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/auth", tags=["auth"])


def _normalize_username(value: str) -> str:
    return value.strip().lower()


def _hash_code(code: str) -> str:
    payload = f"{settings.jwt_secret}:{code}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _generate_otp_code(length: int = 6) -> str:
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))


def _queue_email_verification(db: Session, user: User) -> None:
    code = _generate_otp_code()
    code_hash = _hash_code(code)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.email_verification_expire_minutes
    )

    token = EmailVerificationToken(
        user_id=user.id,
        code_hash=code_hash,
        expires_at=expires_at,
    )
    db.add(token)

    db.add(
        EmailEvent(
            to_email=user.email,
            template="email_verification",
            payload_json={
                "user_id": user.id,
                "username": user.username,
                "code": code,
                "expires_at": expires_at.isoformat(),
            },
        )
    )


def _get_user_for_login(db: Session, data: LoginIn) -> User | None:
    if data.username:
        username = _normalize_username(data.username)
        return (
            db.query(User)
            .filter(User.username == username)
            .first()
        )
    email = data.email.strip().lower() if data.email else None
    if not email:
        return None
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def _get_user_by_identifier(
    db: Session,
    *,
    username: str | None = None,
    email: str | None = None,
) -> User | None:
    clauses = []
    if username:
        clauses.append(User.username == _normalize_username(username))
    if email:
        clauses.append(User.email == email.strip().lower())
    if not clauses:
        return None
    return db.query(User).filter(or_(*clauses) if len(clauses) > 1 else clauses[0]).first()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db_session)) -> UserOut:
    email = data.email.strip().lower()
    username = _normalize_username(data.username)
    enroll_token = data.enroll_token.strip() if data.enroll_token else None

    existing = _get_user_by_identifier(db, username=username, email=email)
    if existing:
        if existing.email == email:
            detail = "Email already registered"
        else:
            detail = "Username already taken"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(data.password),
        role="user",
        status="inactive",
    )
    db.add(user)
    db.flush()

    if enroll_token:
        service = EnrollmentService(db)
        try:
            service.consume_token(enroll_token, user)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    _queue_email_verification(db, user)
    db.commit()

    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: LoginIn, db: Session = Depends(get_db_session)) -> Token:
    user = _get_user_for_login(db, data)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify before signing in.",
        )
    token = create_access_token(
        subject=str(user.id),
        role=user.role,
        organization_id=user.organization_id,
    )
    return Token(access_token=token)


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
def verify_email(data: VerifyEmailIn, db: Session = Depends(get_db_session)) -> Response:
    user = _get_user_by_identifier(db, username=data.username, email=data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.status == "active":
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    latest_token = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used_at.is_(None),
        )
        .order_by(EmailVerificationToken.created_at.desc())
        .first()
    )

    if not latest_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No verification code found"
        )

    now = datetime.now(timezone.utc)
    if latest_token.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code has expired"
        )

    if latest_token.code_hash != _hash_code(data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
        )

    latest_token.used_at = now
    user.status = "active"
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
def resend_verification(
    data: ResendVerificationIn,
    db: Session = Depends(get_db_session),
) -> dict[str, str]:
    user = _get_user_by_identifier(db, username=data.username, email=data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.status == "active":
        return {"detail": "Email already verified"}

    _queue_email_verification(db, user)
    db.commit()
    return {"detail": "Verification email sent"}
