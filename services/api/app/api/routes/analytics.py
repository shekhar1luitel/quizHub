from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_learner
from app.models.attempt import Attempt, AttemptAnswer
from app.models.subject import Subject
from app.models.question import Question
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsOverview,
    SubjectPerformance,
    OverallStats,
    TimeAnalysis,
    WeeklyProgressEntry,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _as_float(value: float | None) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _calculate_streak(attempts: Iterable[Attempt]) -> int:
    unique_dates = sorted({attempt.submitted_at.date() for attempt in attempts})
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


@router.get("/overview", response_model=AnalyticsOverview)
def get_analytics_overview(
    current_user: User = Depends(require_learner),
    db: Session = Depends(get_db_session),
) -> AnalyticsOverview:
    attempts: List[Attempt] = (
        db.query(Attempt)
        .filter(Attempt.user_id == current_user.id)
        .order_by(Attempt.finished_at.asc())
        .all()
    )

    total_tests = len(attempts)
    average_score = _as_float(sum(_as_float(attempt.score) for attempt in attempts) / total_tests) if total_tests else 0.0
    total_time_spent = int(sum(attempt.duration_seconds or 0 for attempt in attempts))

    window = min(5, total_tests) or 1
    early_average = (
        sum(_as_float(attempt.score) for attempt in attempts[:window]) / window
        if attempts
        else 0.0
    )
    recent_average = (
        sum(_as_float(attempt.score) for attempt in attempts[-window:]) / window
        if attempts
        else 0.0
    )
    improvement_rate = round(recent_average - early_average, 2)

    streak = _calculate_streak(attempts)

    weekly_progress_map: Dict[datetime, Dict[str, float]] = defaultdict(lambda: {"tests": 0, "score_sum": 0.0})
    for attempt in attempts:
        date = attempt.submitted_at.astimezone(timezone.utc).date()
        week_start = date - timedelta(days=date.weekday())
        bucket = weekly_progress_map[datetime.combine(week_start, datetime.min.time(), tzinfo=timezone.utc)]
        bucket["tests"] += 1
        bucket["score_sum"] += _as_float(attempt.score)

    weekly_progress = [
        WeeklyProgressEntry(
            label=bucket_date.strftime("Week of %d %b %Y"),
            tests=int(payload["tests"]),
            average_score=round(payload["score_sum"] / payload["tests"], 2) if payload["tests"] else 0.0,
        )
        for bucket_date, payload in sorted(weekly_progress_map.items())
    ]

    total_answered = sum(attempt.total_questions or 0 for attempt in attempts)
    average_time_per_question = (
        (total_time_spent / total_answered) if total_answered else 0.0
    )
    fastest_attempt = min((attempt.duration_seconds or 0 for attempt in attempts), default=0)
    slowest_attempt = max((attempt.duration_seconds or 0 for attempt in attempts), default=0)
    recommended_lower = max(average_time_per_question - 15, 5) if average_time_per_question else 0.0
    recommended_upper = average_time_per_question + 15 if average_time_per_question else 0.0

    time_analysis = None
    if total_tests:
        time_analysis = TimeAnalysis(
            average_time_per_question_seconds=round(average_time_per_question, 2),
            fastest_attempt_seconds=int(fastest_attempt),
            slowest_attempt_seconds=int(slowest_attempt),
            recommended_time_per_question_lower=round(recommended_lower, 2),
            recommended_time_per_question_upper=round(recommended_upper, 2),
        )

    attempt_ids = [attempt.id for attempt in attempts]
    subject_performance: List[SubjectPerformance] = []
    strengths: List[str] = []
    weaknesses: List[str] = []

    if attempt_ids:
        subject_rows = db.execute(
            select(
                Attempt.id.label("attempt_id"),
                Attempt.finished_at.label("submitted_at"),
                Subject.name.label("subject_name"),
                func.count(AttemptAnswer.id).label("answered"),
                func.sum(case((AttemptAnswer.is_correct.is_(True), 1), else_=0)).label("correct"),
            )
            .join(AttemptAnswer, AttemptAnswer.attempt_id == Attempt.id)
            .join(Question, Question.id == AttemptAnswer.question_id)
            .join(Subject, Subject.id == Question.subject_id)
            .where(Attempt.id.in_(attempt_ids))
            .group_by(Attempt.id, Attempt.finished_at, Subject.id)
            .order_by(Subject.name, Attempt.finished_at)
        ).all()

        subject_history: Dict[str, List[tuple[datetime, float]]] = defaultdict(list)
        for row in subject_rows:
            answered = row.answered or 0
            if answered == 0:
                continue
            accuracy = (row.correct or 0) / answered * 100
            subject_history[row.subject_name].append((row.submitted_at, accuracy))

        for subject_name, history in subject_history.items():
            history.sort(key=lambda item: item[0])
            scores = [entry[1] for entry in history]
            average = sum(scores) / len(scores)
            best = max(scores)
            improvement = scores[-1] - scores[0] if len(scores) > 1 else 0.0
            subject_performance.append(
                SubjectPerformance(
                    subject=subject_name,
                    tests=len(history),
                    average_score=round(average, 2),
                    best_score=round(best, 2),
                    improvement=round(improvement, 2),
                )
            )

        subject_performance.sort(key=lambda entry: entry.average_score, reverse=True)

        if subject_performance:
            strengths = [entry.subject for entry in subject_performance if entry.average_score >= 75]
            weaknesses = [entry.subject for entry in subject_performance if entry.average_score < 55]
            strengths = strengths[:3]
            weaknesses = weaknesses[:3]

    overall = OverallStats(
        total_tests=total_tests,
        average_score=round(average_score, 2),
        total_time_spent_seconds=total_time_spent,
        improvement_rate=round(improvement_rate, 2),
        streak=streak,
    )

    return AnalyticsOverview(
        generated_at=datetime.now(timezone.utc),
        overall_stats=overall,
        subject_performance=subject_performance,
        weekly_progress=weekly_progress,
        time_analysis=time_analysis,
        strengths=strengths,
        weaknesses=weaknesses,
    )
