from __future__ import annotations

from typing import Annotated, Dict, List, Set

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db_session, require_learner
from app.core.difficulty import difficulty_label, normalized_difficulty
from app.models.bookmark import Bookmark
from app.models.category import Category
from app.models.question import Question, QuizQuestion
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.practice import (
    PracticeCategoryDetail,
    PracticeCategorySummary,
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


@router.get("/categories", response_model=List[PracticeCategorySummary])
def list_practice_categories(
    current_user: User = Depends(require_learner),
    db: Session = Depends(get_db_session),
) -> List[PracticeCategorySummary]:
    org_id = _resolve_practice_org_id(current_user)

    categories = list(
        db.scalars(
            select(Category)
            .where(
                Category.organization_id == org_id
                if org_id is not None
                else Category.organization_id.is_(None)
            )
            .order_by(Category.name.asc())
        )
    )

    question_rows = db.execute(
        select(Question.category_id, Question.difficulty)
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
            Question.category_id.label("category_id"),
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
        .group_by(Question.category_id, Quiz.id)
    ).all()

    quiz_map: Dict[int, int] = {}
    quiz_counts: Dict[int, int] = {}

    for row in quiz_rows:
        category_id = row.category_id
        question_count = int(row.question_count or 0)
        if category_id is None or question_count == 0:
            continue
        existing_count = quiz_counts.get(category_id, -1)
        if question_count > existing_count:
            quiz_counts[category_id] = question_count
            quiz_map[category_id] = row.quiz_id

    for category_id, difficulty in question_rows:
        if category_id is None:
            continue
        totals[category_id] = totals.get(category_id, 0) + 1
        normalized = normalized_difficulty(difficulty)
        if normalized:
            difficulties_map.setdefault(category_id, set()).add(normalized)

    summaries: List[PracticeCategorySummary] = []
    for category in categories:
        difficulties = sorted(difficulties_map.get(category.id, set()))
        summaries.append(
            PracticeCategorySummary(
                slug=category.slug,
                name=category.name,
                description=category.description,
                icon=category.icon,
                total_questions=totals.get(category.id, 0),
                difficulty=difficulty_label(difficulties),
                difficulties=difficulties,
                quiz_id=quiz_map.get(category.id),
                organization_id=category.organization_id,
            )
        )

    return summaries


@router.get("/categories/{slug}", response_model=PracticeCategoryDetail)
def get_practice_category(
    slug: str,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    current_user: User = Depends(require_learner),
    db: Session = Depends(get_db_session),
) -> PracticeCategoryDetail:
    org_id = _resolve_practice_org_id(current_user)

    category = db.scalar(
        select(Category)
        .where(Category.slug == slug)
        .where(
            Category.organization_id == org_id
            if org_id is not None
            else Category.organization_id.is_(None)
        )
    )
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    stmt = (
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.is_active.is_(True))
        .where(Question.category_id == category.id)
        .order_by(Question.id.desc())
        .limit(limit)
    )
    if category.organization_id is None:
        stmt = stmt.where(Question.organization_id.is_(None))
    else:
        stmt = stmt.where(Question.organization_id == category.organization_id)

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
    return PracticeCategoryDetail(
        slug=category.slug,
        name=category.name,
        description=category.description,
        icon=category.icon,
        total_questions=len(questions),
        difficulty=difficulty_label(difficulties),
        questions=questions_payload,
        organization_id=category.organization_id,
    )


@router.get("/bookmarks", response_model=PracticeCategoryDetail)
def get_bookmark_revision_set(
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    difficulty: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    category_id: Annotated[int | None, Query(ge=1)] = None,
    current_user: User = Depends(require_learner),
    db: Session = Depends(get_db_session),
) -> PracticeCategoryDetail:
    stmt = (
        select(Question)
        .join(Bookmark, Bookmark.question_id == Question.id)
        .options(selectinload(Question.options), selectinload(Question.category))
        .where(Bookmark.user_id == current_user.id)
        .where(Question.is_active.is_(True))
        .order_by(Bookmark.created_at.desc())
    )

    if category_id is not None:
        stmt = stmt.where(Question.category_id == category_id)
    if difficulty:
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

    return PracticeCategoryDetail(
        slug="bookmarks",
        name="Bookmarks revision",
        description="Revisit questions you have saved for a targeted study session.",
        icon="🔖",
        total_questions=len(questions),
        difficulty=difficulty_label(difficulties),
        questions=questions_payload,
        organization_id=current_user.organization_id,
    )
