from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        Index("ix_questions_subject_topic_difficulty", "subject", "topic", "difficulty"),
        Index(
            "ix_questions_fts",
            text("to_tsvector('simple', coalesce(text_en,'') || ' ' || coalesce(text_ne,''))"),
            postgresql_using="gin",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    prompt: Mapped[str] = mapped_column(Text(), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text())
    subject: Mapped[str | None] = mapped_column(String(100))
    topic: Mapped[str | None] = mapped_column(String(100))
    difficulty: Mapped[str | None] = mapped_column(String(50))
    text_en: Mapped[str | None] = mapped_column(Text())
    text_ne: Mapped[str | None] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )

    options: Mapped[List["Option"]] = relationship(
        "Option", back_populates="question", cascade="all, delete-orphan", order_by="Option.id"
    )
    quizzes: Mapped[List["QuizQuestion"]] = relationship(
        "QuizQuestion", back_populates="question", cascade="all, delete-orphan"
    )
    category: Mapped["Category"] = relationship("Category", back_populates="questions")
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        "Bookmark", back_populates="question", cascade="all, delete-orphan"
    )


class Option(Base):
    __tablename__ = "options"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text(), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    question: Mapped[Question] = relationship("Question", back_populates="options")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
    question: Mapped[Question] = relationship("Question", back_populates="quizzes")


__all__ = ["Question", "Option", "QuizQuestion"]
