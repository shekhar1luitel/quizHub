from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Enum, ForeignKey, Index, JSON, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


JSON_DICT = JSON().with_variant(JSONB(astext_type=String()), "postgresql")

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("active", "inactive", name="organization_status_enum", native_enum=False),
        nullable=False,
        default="active",
        server_default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    users: Mapped[List["User"]] = relationship("User", back_populates="organization")
    memberships: Mapped[List["OrgMembership"]] = relationship(
        "OrgMembership", back_populates="organization", cascade="all, delete-orphan"
    )
    enroll_tokens: Mapped[List["EnrollToken"]] = relationship(
        "EnrollToken", back_populates="organization", cascade="all, delete-orphan"
    )
    configs: Mapped[List["AppConfig"]] = relationship(
        "AppConfig", back_populates="organization", cascade="all, delete-orphan"
    )
    organization_accounts: Mapped[List["OrganizationUser"]] = relationship(
        "OrganizationUser", back_populates="organization", cascade="all, delete-orphan"
    )
    learner_accounts: Mapped[List["LearnerUser"]] = relationship(
        "LearnerUser", back_populates="primary_organization", cascade="all, delete-orphan"
    )
    subjects: Mapped[List["Subject"]] = relationship(
        "Subject", back_populates="organization", cascade="all, delete-orphan"
    )
    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="organization", cascade="all, delete-orphan"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    student_id: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    qr_code_uri: Mapped[str | None] = mapped_column(String(512), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="profile")


class OrgMembership(Base):
    __tablename__ = "org_memberships"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_membership_org_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    org_role: Mapped[str] = mapped_column(
        Enum("org_admin", "instructor", "member", name="org_membership_role", native_enum=False),
        nullable=False,
        default="member",
        server_default="member",
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "invited", name="org_membership_status", native_enum=False),
        nullable=False,
        default="active",
        server_default="active",
    )

    organization: Mapped[Organization] = relationship("Organization", back_populates="memberships")
    user: Mapped["User"] = relationship("User", back_populates="memberships")


class EnrollToken(Base):
    __tablename__ = "enroll_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    organization: Mapped[Organization] = relationship("Organization", back_populates="enroll_tokens")
    used_by: Mapped["User | None"] = relationship("User", foreign_keys=[used_by_user_id])


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_created", "user_id", text("created_at DESC")),
        Index("ix_notifications_user_read", "user_id", "read_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(String(1024), nullable=False)
    meta_json: Mapped[dict | None] = mapped_column(JSON_DICT, nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="notifications")


class EmailEvent(Base):
    __tablename__ = "email_events"
    __table_args__ = (
        Index("ix_email_events_status_created", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    template: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_json: Mapped[dict | None] = mapped_column(JSON_DICT, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("queued", "sent", "failed", name="email_event_status", native_enum=False),
        nullable=False,
        default="queued",
        server_default="queued",
    )
    error_msg: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AppConfig(Base):
    __tablename__ = "app_configs"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value_json: Mapped[dict | None] = mapped_column(JSON_DICT, nullable=True)
    scope: Mapped[str] = mapped_column(
        Enum("global", "org", name="app_config_scope", native_enum=False),
        nullable=False,
        default="global",
        server_default="global",
    )
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    organization: Mapped[Organization | None] = relationship("Organization", back_populates="configs")


__all__ = [
    "Organization",
    "UserProfile",
    "OrgMembership",
    "EnrollToken",
    "Notification",
    "EmailEvent",
    "AppConfig",
]
