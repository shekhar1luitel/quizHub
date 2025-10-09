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
    return current_user


def require_admin(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role not in {"admin", "superuser"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def require_org_admin_or_superuser(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role not in {"org_admin", "superuser"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Org admin access required")
    return current_user


def require_user(current_user: User = Depends(require_active_user)) -> User:
    return current_user


def get_current_org_id(token: dict = Depends(get_current_token)) -> int | None:
    organization_id = token.get("organization_id")
    if organization_id is None:
        return None
    try:
        return int(organization_id)
    except (TypeError, ValueError):
        return None
