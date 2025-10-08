from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_db_session
from app.models.attempt import Attempt
from app.models.user import User
from app.schemas.dashboard import AttemptSummary, DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> DashboardSummary:
    aggregate = (
        db.query(
            func.count(Attempt.id),
            func.coalesce(func.avg(Attempt.score), 0),
            func.coalesce(func.sum(Attempt.correct_answers), 0),
            func.coalesce(func.sum(Attempt.total_questions), 0),
        )
        .filter(Attempt.user_id == current_user.id)
        .one()
    )

    recent_attempts = (
        db.query(Attempt)
        .options(selectinload(Attempt.quiz))
        .filter(Attempt.user_id == current_user.id)
        .order_by(Attempt.submitted_at.desc())
        .limit(5)
        .all()
    )

    return DashboardSummary(
        total_attempts=aggregate[0],
        average_score=float(aggregate[1]) if aggregate[0] else 0.0,
        total_correct_answers=int(aggregate[2] or 0),
        total_questions_answered=int(aggregate[3] or 0),
        recent_attempts=[
            AttemptSummary(
                id=attempt.id,
                quiz_id=attempt.quiz_id,
                quiz_title=attempt.quiz.title if attempt.quiz else "",
                score=float(attempt.score),
                submitted_at=attempt.submitted_at,
            )
            for attempt in recent_attempts
        ],
    )
