from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


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


class UserProfileOut(BaseModel):
    name: str | None
    phone: str | None
    student_id: str | None
    qr_code_uri: str | None
    avatar_url: str | None

    class Config:
        from_attributes = True


class OrganizationSummary(BaseModel):
    id: int
    name: str
    slug: str
    type: str | None = None
    logo_url: str | None = None

    class Config:
        from_attributes = True


class OrgMembershipSummary(BaseModel):
    id: int
    org_role: str
    status: str
    organization: OrganizationSummary

    class Config:
        from_attributes = True


class PlatformAccountOut(BaseModel):
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationAccountOut(BaseModel):
    organization_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class LearnerAccountOut(BaseModel):
    primary_org_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetailOut(UserOut):
    profile: UserProfileOut | None = None
    organization: OrganizationSummary | None = None
    memberships: list[OrgMembershipSummary] = Field(default_factory=list)
    platform_account: PlatformAccountOut | None = None
    organization_account: OrganizationAccountOut | None = None
    learner_account: LearnerAccountOut | None = None


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=150)
    email: EmailStr | None = None
    name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    avatar_url: str | None = Field(default=None, max_length=512)
    current_password: str | None = Field(default=None, min_length=8, max_length=256)
    new_password: str | None = Field(default=None, min_length=8, max_length=256)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Username is required")
        return cleaned

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("avatar_url")
    @classmethod
    def normalize_avatar_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr | None) -> EmailStr | None:
        if value is None:
            return None
        return EmailStr(str(value).strip().lower())

    @field_validator("current_password")
    @classmethod
    def strip_current_password(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("new_password")
    @classmethod
    def strip_new_password(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def validate_password_change(self) -> "UserUpdate":
        if self.new_password and not self.current_password:
            raise ValueError("Current password is required to set a new password")
        return self
