from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "status": current_user.status,
        "account_type": current_user.account_type,
        "organization_id": current_user.organization_id,
    }
