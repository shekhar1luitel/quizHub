from __future__ import annotations

from datetime import datetime
from typing import Sequence

from pydantic import BaseModel, EmailStr, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    type: str | None = Field(default=None, max_length=50)


class OrganizationOut(BaseModel):
    id: int
    name: str
    slug: str
    type: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class EnrollTokenCreateIn(BaseModel):
    expires_in_minutes: int = Field(default=24 * 60, ge=5, le=60 * 24 * 30)


class EnrollTokenCreateOut(BaseModel):
    token: str
    expires_at: datetime


class OrganizationEnrollIn(BaseModel):
    token: str = Field(min_length=8, max_length=255)


class OrgMemberOut(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    role: str
    account_type: str
    org_role: str
    status: str


class OrgMemberListResponse(BaseModel):
    items: Sequence[OrgMemberOut]
    total: int
