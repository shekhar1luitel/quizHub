from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_org_status", "organization_id", "status"),
        Index("ix_users_account_type", "account_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("superuser", "org_admin", "admin", "user", name="user_role", native_enum=False),
        nullable=False,
        default="user",
        server_default="user",
    )
    account_type: Mapped[str] = mapped_column(
        Enum(
            "individual",
            "organization_admin",
            "organization_member",
            "staff",
            name="user_account_type",
            native_enum=False,
        ),
        nullable=False,
        default="individual",
        server_default="individual",
    )
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "inactive", name="user_status", native_enum=False),
        nullable=False,
        default="active",
        server_default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    organization: Mapped["Organization | None"] = relationship("Organization", back_populates="users")
    profile: Mapped["UserProfile | None"] = relationship(
        "UserProfile", back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    memberships: Mapped[List["OrgMembership"]] = relationship(
        "OrgMembership", back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    attempts: Mapped[List["Attempt"]] = relationship(
        "Attempt", back_populates="user", cascade="all, delete-orphan"
    )
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        "Bookmark", back_populates="user", cascade="all, delete-orphan"
    )
    verification_tokens: Mapped[List["EmailVerificationToken"]] = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="EmailVerificationToken.created_at.desc()",
    )


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="verification_tokens")
