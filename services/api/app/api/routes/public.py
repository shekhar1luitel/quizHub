from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db_session
from app.core.difficulty import difficulty_label, normalized_difficulty
from app.models.attempt import Attempt
from app.models.category import Category
from app.models.question import Question, QuizQuestion
from app.models.quiz import Quiz
from app.schemas.public import (
    PublicCategorySummary,
    PublicHomeResponse,
    PublicQuizSummary,
)
from app.schemas.topic import TopicOut

router = APIRouter(prefix="/public", tags=["public"])


def _global_categories(db: Session, limit: int) -> List[PublicCategorySummary]:
    categories = list(
        db.scalars(
            select(Category)
            .options(selectinload(Category.topics))
            .where(Category.organization_id.is_(None))
            .order_by(Category.name.asc())
            .limit(limit)
        )
    )

    question_counts = dict(
        db.execute(
            select(Question.category_id, func.count(Question.id))
            .where(Question.organization_id.is_(None))
            .where(Question.is_active.is_(True))
            .group_by(Question.category_id)
        ).all()
    )

    difficulties = {}
    difficulty_rows = db.execute(
        select(Question.category_id, Question.difficulty)
        .where(Question.organization_id.is_(None))
        .where(Question.is_active.is_(True))
    ).all()
    for category_id, raw_difficulty in difficulty_rows:
        if category_id is None:
            continue
        normalized = normalized_difficulty(raw_difficulty)
        if normalized:
            difficulties.setdefault(category_id, set()).add(normalized)

    summaries: List[PublicCategorySummary] = []
    for category in categories:
        totals = int(question_counts.get(category.id, 0))
        normalized_list = sorted(difficulties.get(category.id, set()))
        summaries.append(
            PublicCategorySummary(
                slug=category.slug,
                name=category.name,
                description=category.description,
                icon=category.icon,
                total_questions=totals,
                difficulty=difficulty_label(normalized_list),
                topics=[TopicOut.model_validate(topic) for topic in category.topics],
            )
        )
    return summaries


def _trending_quizzes(db: Session, limit: int) -> List[PublicQuizSummary]:
    attempt_counts = dict(
        db.execute(
            select(Attempt.quiz_id, func.count(Attempt.id))
            .join(Quiz, Quiz.id == Attempt.quiz_id)
            .where(Quiz.is_active.is_(True))
            .where(Quiz.organization_id.is_(None))
            .group_by(Attempt.quiz_id)
        ).all()
    )

    question_counts = dict(
        db.execute(
            select(QuizQuestion.quiz_id, func.count(QuizQuestion.question_id))
            .group_by(QuizQuestion.quiz_id)
        ).all()
    )

    quizzes = list(
        db.scalars(
            select(Quiz)
            .where(Quiz.is_active.is_(True))
            .where(Quiz.organization_id.is_(None))
            .order_by(desc(Quiz.created_at))
            .limit(limit * 2)
        )
    )

    # sort locally to prioritise attempts, then recent ones
    quizzes.sort(
        key=lambda quiz: (
            attempt_counts.get(quiz.id, 0),
            quiz.created_at,
        ),
        reverse=True,
    )

    summaries: List[PublicQuizSummary] = []
    for quiz in quizzes[:limit]:
        summaries.append(
            PublicQuizSummary(
                id=quiz.id,
                title=quiz.title,
                description=quiz.description,
                question_count=int(question_counts.get(quiz.id, 0)),
                total_attempts=int(attempt_counts.get(quiz.id, 0)),
                created_at=quiz.created_at,
            )
        )
    return summaries


@router.get("/home", response_model=PublicHomeResponse)
def get_public_home(
    limit: int = Query(default=6, ge=1, le=24),
    db: Session = Depends(get_db_session),
) -> PublicHomeResponse:
    categories = _global_categories(db, limit)
    quizzes = _trending_quizzes(db, limit)
    return PublicHomeResponse(featured_categories=categories, trending_quizzes=quizzes)
