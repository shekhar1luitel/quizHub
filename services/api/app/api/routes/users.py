from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def me():
    # Placeholder; in real app parse JWT and fetch user
    return {"id": 1, "email": "demo@example.com", "role": "user"}
