from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint("subject_id", "slug", name="uq_topics_subject_slug"),
        UniqueConstraint("subject_id", "name", name="uq_topics_subject_name"),
        Index("ix_topics_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text())

    subject: Mapped["Category"] = relationship("Category", back_populates="topics")
    _questions: Mapped[list["Question"]] = relationship("Question", back_populates="_topic")


__all__ = ["Topic"]
