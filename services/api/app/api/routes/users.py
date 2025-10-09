from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db_session, require_user
from app.core.security import get_password_hash, verify_password
from app.models.organization import OrgMembership, UserProfile
from app.models.user import LearnerUser, OrganizationUser, User
from app.schemas.user import UserDetailOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _load_current_user(db: Session, user_id: int) -> User:
    user = (
        db.query(User)
        .options(
            selectinload(User.profile),
            selectinload(User.organization),
            selectinload(User.memberships).selectinload(OrgMembership.organization),
            selectinload(User.platform_account),
            selectinload(User.organization_account).selectinload(OrganizationUser.organization),
            selectinload(User.learner_account).selectinload(LearnerUser.primary_organization),
        )
        .filter(User.id == user_id)
        .first()
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/me", response_model=UserDetailOut)
def me(
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db_session),
) -> UserDetailOut:
    user = _load_current_user(db, current_user.id)
    return UserDetailOut.model_validate(user, from_attributes=True)


@router.patch("/me", response_model=UserDetailOut)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db_session),
) -> UserDetailOut:
    user = _load_current_user(db, current_user.id)

    if payload.username and payload.username != user.username:
        existing = (
            db.query(User)
            .filter(User.username == payload.username)
            .first()
        )
        if existing and existing.id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        user.username = payload.username

    if payload.email and payload.email != user.email:
        existing = (
            db.query(User)
            .filter(User.email == payload.email)
            .first()
        )
        if existing and existing.id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user.email = str(payload.email)

    if payload.new_password:
        if not payload.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to set a new password",
            )
        if not verify_password(payload.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        user.hashed_password = get_password_hash(payload.new_password)

    profile = user.profile
    if profile is None and any(field is not None for field in (payload.name, payload.phone, payload.avatar_url)):
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.flush()
        user.profile = profile

    if profile:
        if payload.name is not None:
            profile.name = payload.name
        if payload.phone is not None:
            profile.phone = payload.phone
        if payload.avatar_url is not None:
            profile.avatar_url = payload.avatar_url or None

    db.commit()
    refreshed = _load_current_user(db, user.id)
    return UserDetailOut.model_validate(refreshed, from_attributes=True)
