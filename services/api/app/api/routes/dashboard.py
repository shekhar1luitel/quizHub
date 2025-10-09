from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db_session, require_learner
from app.models.attempt import Attempt, AttemptAnswer
from app.models.category import Category
from app.models.question import Question
from app.models.user import User
from app.schemas.dashboard import (
    AttemptSummary,
    CategoryAccuracy,
    DashboardSummary,
    WeeklyActivityEntry,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _calculate_streak(attempts: list[Attempt]) -> int:
    unique_dates = sorted(
        {attempt.submitted_at.astimezone(timezone.utc).date() for attempt in attempts}
    )
    if not unique_dates:
        return 0

    streak = 1
    for index in range(len(unique_dates) - 1, 0, -1):
        gap = (unique_dates[index] - unique_dates[index - 1]).days
        if gap == 1:
            streak += 1
        elif gap > 1:
            break
    return streak


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(require_learner),
    db: Session = Depends(get_db_session),
) -> DashboardSummary:
    attempts: list[Attempt] = (
        db.query(Attempt)
        .options(selectinload(Attempt.quiz))
        .filter(Attempt.user_id == current_user.id)
        .order_by(Attempt.finished_at.desc())
        .all()
    )

    total_attempts = len(attempts)
    total_correct = sum(int(attempt.correct_answers or 0) for attempt in attempts)
    total_questions = sum(int(attempt.total_questions or 0) for attempt in attempts)
    average_score = (
        float(sum(float(attempt.score or 0) for attempt in attempts) / total_attempts)
        if total_attempts
        else 0.0
    )

    recent_attempts = attempts[:5]
    streak = _calculate_streak(attempts)

    weekly_map: dict[datetime, int] = defaultdict(int)
    for attempt in attempts:
        date = attempt.submitted_at.astimezone(timezone.utc).date()
        week_start = date - timedelta(days=date.weekday())
        bucket = datetime.combine(week_start, datetime.min.time(), tzinfo=timezone.utc)
        weekly_map[bucket] += 1

    weekly_activity: list[WeeklyActivityEntry] = [
        WeeklyActivityEntry(
            label=bucket_date.strftime("Week of %d %b"),
            attempts=count,
        )
        for bucket_date, count in sorted(weekly_map.items())
    ]

    category_accuracy: list[CategoryAccuracy] = []
    attempt_ids = [attempt.id for attempt in attempts]
    if attempt_ids:
        rows = db.execute(
            select(
                Question.category_id.label("category_id"),
                func.count(func.distinct(AttemptAnswer.attempt_id)).label("attempts"),
                func.count(AttemptAnswer.id).label("answered"),
                func.sum(case((AttemptAnswer.is_correct.is_(True), 1), else_=0)).label("correct"),
            )
            .join(Question, Question.id == AttemptAnswer.question_id)
            .where(AttemptAnswer.attempt_id.in_(attempt_ids))
            .group_by(Question.category_id)
        ).all()

        category_ids = [row.category_id for row in rows if row.category_id is not None]
        category_lookup = {}
        if category_ids:
            category_lookup = dict(
                db.execute(
                    select(Category.id, Category.name).where(Category.id.in_(category_ids))
                ).all()
            )

        for row in rows:
            attempts_count = int(row.attempts or 0)
            answered = int(row.answered or 0)
            correct = int(row.correct or 0)
            if answered == 0:
                continue
            category_id = row.category_id
            category_name = (
                category_lookup.get(category_id)
                if category_id is not None
                else "General Practice"
            )
            average = (correct / answered) * 100 if answered else 0.0
            category_accuracy.append(
                CategoryAccuracy(
                    category_id=category_id,
                    category_name=category_name or "General Practice",
                    attempts=attempts_count,
                    average_score=round(average, 2),
                )
            )

        category_accuracy.sort(key=lambda entry: entry.average_score, reverse=True)

    return DashboardSummary(
        total_attempts=total_attempts,
        average_score=round(average_score, 2),
        total_correct_answers=total_correct,
        total_questions_answered=total_questions,
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
        streak=streak,
        category_accuracy=category_accuracy,
        weekly_activity=weekly_activity[-12:],
    )
