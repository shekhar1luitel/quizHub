from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User


security_scheme = HTTPBearer(auto_error=False)


def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db


def get_current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        return decode_token(credentials.credentials)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None


def get_current_user(
    token: dict = Depends(get_current_token),
    db: Session = Depends(get_db_session),
) -> User:
    try:
        user_id = int(token["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user = db.get(User, user_id)
    if not user or user.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    setattr(user, "token_claims", token)
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db_session),
) -> User | None:
    if credentials is None:
        return None
    try:
        token = decode_token(credentials.credentials)
    except Exception:  # noqa: BLE001
        return None
    try:
        user_id = int(token["sub"])
    except (KeyError, TypeError, ValueError):
        return None
    user = db.get(User, user_id)
    if not user:
        return None
    setattr(user, "token_claims", token)
    return user


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")
    if (
        current_user.role != "superuser"
        and current_user.organization is not None
        and current_user.organization.status != "active"
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization is disabled")
    return current_user


def require_superuser(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role != "superuser":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser access required")
    if current_user.platform_account is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Platform user record missing")
    return current_user


def require_admin(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role not in {"admin", "superuser"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    if current_user.role == "admin" and current_user.platform_account is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Platform user record missing")
    return current_user


def require_org_admin_or_superuser(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role not in {"org_admin", "superuser"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Org admin access required")
    if current_user.role == "org_admin" and current_user.organization_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization not assigned")
    return current_user


def require_content_manager(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role not in {"org_admin", "admin", "superuser"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Content access denied")
    if current_user.role == "org_admin" and current_user.organization_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization not assigned")
    if current_user.role == "admin" and current_user.platform_account is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Platform user record missing")
    return current_user


def require_user(current_user: User = Depends(require_active_user)) -> User:
    return current_user


def require_learner(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role != "user" or current_user.learner_account is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Learner access required")
    return current_user


def get_current_org_id(token: dict = Depends(get_current_token)) -> int | None:
    organization_id = token.get("organization_id")
    if organization_id is None:
        return None
    try:
        return int(organization_id)
    except (TypeError, ValueError):
        return None


def resolve_content_organization(
    current_user: User,
    organization_id: int | None,
    *,
    allow_global_for_admin: bool = False,
) -> int | None:
    if current_user.role == "org_admin":
        org_id = current_user.organization_id
        if org_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization not assigned")
        if organization_id is not None and organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot target another organization")
        return org_id

    if current_user.role == "admin":
        if organization_id is None:
            if allow_global_for_admin:
                return None
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="organization_id is required for admin scope",
            )
        return organization_id

    if current_user.role == "superuser":
        return organization_id

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Content access denied")
