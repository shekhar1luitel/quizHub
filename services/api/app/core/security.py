from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import hashlib
import jwt

from app.core.config import settings


def _normalized_password(password: str) -> bytes:
    """Ensure consistent hashing input and avoid bcrypt's 72 byte limit."""
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return digest.encode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    hashed_bytes = hashed_password.encode("utf-8")

    try:
        if bcrypt.checkpw(_normalized_password(plain_password), hashed_bytes):
            return True
    except ValueError:
        return False

    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_bytes)
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(_normalized_password(password), bcrypt.gensalt()).decode("ascii")

def create_jwt_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_jwt_token(token: str) -> str:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    subject = payload.get("sub")
    if subject is None:
        raise ValueError("Token missing subject")
    return subject
