from __future__ import annotations

from typing import Annotated, Dict, List, Set

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.params import Query as QueryParam
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db_session, require_learner
from app.core.difficulty import difficulty_label, normalized_difficulty
from app.models.bookmark import Bookmark
from app.models.subject import Subject
from app.models.question import Question, QuizQuestion
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.practice import (
    PracticeSubjectDetail,
    PracticeSubjectSummary,
    PracticeQuestion,
    PracticeQuestionOption,
)

router = APIRouter(prefix="/practice", tags=["practice"])


def _resolve_practice_org_id(user: User) -> int | None:
    if user.organization_id is not None:
        return user.organization_id
    learner_account = user.learner_account
    if learner_account and learner_account.primary_org_id is not None:
        return learner_account.primary_org_id
    return None


@router.get("/subjects", response_model=List[PracticeSubjectSummary])
def list_practice_subjects(
    current_user: User = Depends(require_learner),
    db: Session = Depends(get_db_session),
) -> List[PracticeSubjectSummary]:
    org_id = _resolve_practice_org_id(current_user)

    subjects = list(
        db.scalars(
            select(Subject)
            .where(
                Subject.organization_id == org_id
                if org_id is not None
                else Subject.organization_id.is_(None)
            )
            .order_by(Subject.name.asc())
        )
    )

    question_rows = db.execute(
        select(Question.subject_id, Question.difficulty)
        .where(Question.is_active.is_(True))
        .where(
            Question.organization_id == org_id
            if org_id is not None
            else Question.organization_id.is_(None)
        )
    ).all()

    totals: Dict[int, int] = {}
    difficulties_map: Dict[int, Set[str]] = {}

    quiz_rows = db.execute(
        select(
            Question.subject_id.label("subject_id"),
            Quiz.id.label("quiz_id"),
            func.count(QuizQuestion.question_id).label("question_count"),
        )
        .join(QuizQuestion, QuizQuestion.question_id == Question.id)
        .join(Quiz, Quiz.id == QuizQuestion.quiz_id)
        .where(Question.is_active.is_(True))
        .where(Quiz.is_active.is_(True))
        .where(
            Question.organization_id == org_id
            if org_id is not None
            else Question.organization_id.is_(None)
        )
        .where(
            Quiz.organization_id == org_id
            if org_id is not None
            else Quiz.organization_id.is_(None)
        )
        .group_by(Question.subject_id, Quiz.id)
    ).all()

    quiz_map: Dict[int, int] = {}
    quiz_counts: Dict[int, int] = {}

    for row in quiz_rows:
        subject_id = row.subject_id
        question_count = int(row.question_count or 0)
        if subject_id is None or question_count == 0:
            continue
        existing_count = quiz_counts.get(subject_id, -1)
        if question_count > existing_count:
            quiz_counts[subject_id] = question_count
            quiz_map[subject_id] = row.quiz_id

    for subject_id, difficulty in question_rows:
        if subject_id is None:
            continue
        totals[subject_id] = totals.get(subject_id, 0) + 1
        normalized = normalized_difficulty(difficulty)
        if normalized:
            difficulties_map.setdefault(subject_id, set()).add(normalized)

    summaries: List[PracticeSubjectSummary] = []
    for subject in subjects:
        difficulties = sorted(difficulties_map.get(subject.id, set()))
        summaries.append(
            PracticeSubjectSummary(
                slug=subject.slug,
                name=subject.name,
                description=subject.description,
                icon=subject.icon,
                total_questions=totals.get(subject.id, 0),
                difficulty=difficulty_label(difficulties),
                difficulties=difficulties,
                quiz_id=quiz_map.get(subject.id),
                organization_id=subject.organization_id,
            )
        )

    return summaries


@router.get("/subjects/{slug}", response_model=PracticeSubjectDetail)
def get_practice_subject(
    slug: str,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    current_user: User = Depends(require_learner),
    db: Session = Depends(get_db_session),
) -> PracticeSubjectDetail:
    org_id = _resolve_practice_org_id(current_user)

    subject = db.scalar(
        select(Subject)
        .where(Subject.slug == slug)
        .where(
            Subject.organization_id == org_id
            if org_id is not None
            else Subject.organization_id.is_(None)
        )
    )
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    stmt = (
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.is_active.is_(True))
        .where(Question.subject_id == subject.id)
        .order_by(Question.id.desc())
        .limit(limit)
    )
    if subject.organization_id is None:
        stmt = stmt.where(Question.organization_id.is_(None))
    else:
        stmt = stmt.where(Question.organization_id == subject.organization_id)

    questions = list(db.scalars(stmt))

    questions_payload = [
        PracticeQuestion(
            id=question.id,
            prompt=question.prompt,
            explanation=question.explanation,
            difficulty=question.difficulty,
            options=[
                PracticeQuestionOption(
                    id=option.id,
                    text=option.text,
                    is_correct=option.is_correct,
                )
                for option in question.options
            ],
        )
        for question in questions
    ]

    difficulties = [
        normalized
        for question in questions
        for normalized in [normalized_difficulty(question.difficulty)]
        if normalized
    ]
    return PracticeSubjectDetail(
        slug=subject.slug,
        name=subject.name,
        description=subject.description,
        icon=subject.icon,
        total_questions=len(questions),
        difficulty=difficulty_label(difficulties),
        questions=questions_payload,
        organization_id=subject.organization_id,
    )


@router.get("/bookmarks", response_model=PracticeSubjectDetail)
def get_bookmark_revision_set(
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    difficulty: str | None = Query(default=None, min_length=1, max_length=50),
    subject_id: int | None = Query(default=None, ge=1),
    current_user: User = Depends(require_learner),
    db: Session = Depends(get_db_session),
) -> PracticeSubjectDetail:
    stmt = (
        select(Question)
        .join(Bookmark, Bookmark.question_id == Question.id)
        .options(selectinload(Question.options), selectinload(Question.subject))
        .where(Bookmark.user_id == current_user.id)
        .where(Question.is_active.is_(True))
        .order_by(Bookmark.created_at.desc())
    )

    if isinstance(subject_id, QueryParam):
        subject_id = subject_id.default
    if isinstance(difficulty, QueryParam):
        difficulty = difficulty.default

    if subject_id is not None:
        stmt = stmt.where(Question.subject_id == subject_id)
    if isinstance(difficulty, str) and difficulty:
        normalized_diff = difficulty.strip().lower()
        if normalized_diff:
            stmt = stmt.where(func.lower(Question.difficulty) == normalized_diff)

    questions = list(db.scalars(stmt.limit(limit)))

    questions_payload = [
        PracticeQuestion(
            id=question.id,
            prompt=question.prompt,
            explanation=question.explanation,
            difficulty=question.difficulty,
            options=[
                PracticeQuestionOption(
                    id=option.id,
                    text=option.text,
                    is_correct=option.is_correct,
                )
                for option in question.options
            ],
        )
        for question in questions
    ]

    difficulties = [
        normalized
        for question in questions
        for normalized in [normalized_difficulty(question.difficulty)]
        if normalized
    ]

    return PracticeSubjectDetail(
        slug="bookmarks",
        name="Bookmarks revision",
        description="Revisit questions you have saved for a targeted study session.",
        icon="🔖",
        total_questions=len(questions),
        difficulty=difficulty_label(difficulties),
        questions=questions_payload,
        organization_id=current_user.organization_id,
    )
