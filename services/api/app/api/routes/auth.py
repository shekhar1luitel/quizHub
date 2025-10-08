from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.security import create_jwt_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import LoginIn, Token
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db_session)) -> UserOut:
    email = data.email.strip().lower()

    user = User(email=email, hashed_password=get_password_hash(data.password))
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:  # pragma: no cover - extra guard for race conditions
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        ) from exc

    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(data: LoginIn, db: Session = Depends(get_db_session)) -> Token:
    email = data.email.strip().lower()

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_jwt_token(str(user.id))
    return Token(access_token=token)
