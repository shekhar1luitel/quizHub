from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin
from app.models.category import Category
from app.models.question import Question, QuizQuestion
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.admin import AdminCategorySnapshot, AdminOverview, AdminRecentQuiz, AdminTotals

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=AdminOverview)
def get_admin_overview(
    _: None = Depends(require_admin),
    db: Session = Depends(get_db_session),
) -> AdminOverview:
    totals = AdminTotals(
        total_quizzes=int(db.scalar(select(func.count()).select_from(Quiz)) or 0),
        active_quizzes=int(
            db.scalar(select(func.count()).select_from(Quiz).where(Quiz.is_active.is_(True))) or 0
        ),
        total_questions=int(db.scalar(select(func.count()).select_from(Question)) or 0),
        inactive_questions=int(
            db.scalar(select(func.count()).select_from(Question).where(Question.is_active.is_(False))) or 0
        ),
        total_categories=int(db.scalar(select(func.count()).select_from(Category)) or 0),
        total_users=int(db.scalar(select(func.count()).select_from(User)) or 0),
    )

    recent_rows = db.execute(
        select(
            Quiz.id,
            Quiz.title,
            Quiz.is_active,
            Quiz.created_at,
            func.count(QuizQuestion.question_id).label("question_count"),
        )
        .join(QuizQuestion, QuizQuestion.quiz_id == Quiz.id, isouter=True)
        .group_by(Quiz.id)
        .order_by(Quiz.created_at.desc())
        .limit(8)
    ).all()

    recent_quizzes: List[AdminRecentQuiz] = [
        AdminRecentQuiz(
            id=row.id,
            title=row.title,
            question_count=int(row.question_count or 0),
            is_active=bool(row.is_active),
            created_at=row.created_at,
        )
        for row in recent_rows
    ]

    top_category_rows = db.execute(
        select(
            Category.id,
            Category.name,
            func.count(Question.id).label("question_count"),
        )
        .join(Question, Question.category_id == Category.id, isouter=True)
        .group_by(Category.id)
        .order_by(func.count(Question.id).desc(), Category.name.asc())
        .limit(6)
    ).all()

    top_categories = [
        AdminCategorySnapshot(
            id=row.id,
            name=row.name,
            question_count=int(row.question_count or 0),
        )
        for row in top_category_rows
    ]

    return AdminOverview(
        totals=totals,
        recent_quizzes=recent_quizzes,
        top_categories=top_categories,
    )
