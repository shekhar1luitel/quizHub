from __future__ import annotations

from datetime import datetime
from typing import Literal, Sequence

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class AdminUserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    role: Literal["admin", "org_admin", "superuser"]
    organization_id: int | None = Field(
        default=None,
        description="Required when role is org_admin.",
    )
    send_invite_email: bool = Field(
        default=True,
        description="If true, queue an email notification for the new user.",
    )
    send_notification: bool = Field(
        default=True,
        description="If true, create an in-app notification for the new user.",
    )

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Username is required")
        return cleaned


class AdminUserStatusUpdate(BaseModel):
    status: Literal["active", "inactive"]


class AdminUserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    status: str
    account_type: str
    organization_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    items: Sequence[AdminUserOut]
    total: int


class MailConfigIn(BaseModel):
    host: str | None = Field(default=None, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    username: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)
    tls_ssl: bool = Field(default=True)
    from_name: str | None = Field(default=None, max_length=255)
    from_email: EmailStr | None = None


class MailConfigOut(MailConfigIn):
    is_configured: bool


class EmailDispatchResult(BaseModel):
    processed: int
    sent: int
    failed: int
    errors: list[str] = Field(default_factory=list)


class AdminNotificationCreate(BaseModel):
    type: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=1024)
    user_ids: list[int] | None = None
    organization_id: int | None = None
    meta: dict | None = None

    @model_validator(mode="after")
    def ensure_target(self) -> "AdminNotificationCreate":
        if (not self.user_ids or len(self.user_ids) == 0) and not self.organization_id:
            raise ValueError("Provide user_ids or organization_id to target notifications.")
        return self


class AdminNotificationResult(BaseModel):
    notified_users: int
