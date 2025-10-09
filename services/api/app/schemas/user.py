from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=256,
        description="Passwords must be between 8 and 256 characters.",
    )
    enroll_token: str | None = Field(
        default=None,
        min_length=8,
        max_length=255,
        description="Optional organization enrollment token.",
    )

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Username is required")
        return cleaned


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    status: str
    account_type: Literal[
        "individual",
        "organization_admin",
        "organization_member",
        "staff",
    ]
    organization_id: int | None

    class Config:
        from_attributes = True
