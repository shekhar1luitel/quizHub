from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("organization_id", "slug", name="uq_categories_org_slug"),
        UniqueConstraint("organization_id", "name", name="uq_categories_org_name"),
        Index("ix_categories_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text())
    icon: Mapped[str | None] = mapped_column(String(16))
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )

    questions: Mapped[list["Question"]] = relationship(
        "Question", back_populates="category"
    )
    organization: Mapped["Organization | None"] = relationship(
        "Organization", back_populates="categories"
    )


__all__ = ["Category"]
