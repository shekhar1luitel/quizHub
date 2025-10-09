from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_BCRYPT_LIMIT = 72


def _truncate_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) <= _BCRYPT_LIMIT:
        return password
    return password_bytes[:_BCRYPT_LIMIT].decode("utf-8", errors="ignore")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = _truncate_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    password = _truncate_password(password)
    return pwd_context.hash(password)


def _build_claims(subject: str, *, role: str, organization_id: int | None) -> Dict[str, Any]:
    claims: Dict[str, Any] = {"sub": subject, "role": role}
    if organization_id is not None:
        claims["organization_id"] = organization_id
    return claims


def create_access_token(*, subject: str, role: str, organization_id: int | None) -> str:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = _build_claims(subject, role=role, organization_id=organization_id)
    to_encode["exp"] = expire
    to_encode["type"] = "access"
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)


def create_refresh_token(*, subject: str, role: str, organization_id: int | None) -> str:
    expires_delta = timedelta(minutes=settings.refresh_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = _build_claims(subject, role=role, organization_id=organization_id)
    to_encode["exp"] = expire
    to_encode["type"] = "refresh"
    return jwt.encode(to_encode, settings.effective_jwt_refresh_secret, algorithm=settings.jwt_alg)


def decode_token(token: str, *, refresh: bool = False) -> Dict[str, Any]:
    secret = settings.effective_jwt_refresh_secret if refresh else settings.jwt_secret
    payload = jwt.decode(token, secret, algorithms=[settings.jwt_alg])
    if payload.get("sub") is None:
        raise ValueError("Token missing subject")
    token_type = payload.get("type")
    expected = "refresh" if refresh else "access"
    if token_type != expected:
        raise ValueError("Invalid token type")
    return payload
