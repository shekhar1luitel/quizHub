from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set

from typing import Dict, List, Optional, Sequence, Set

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db_session
from app.models.category import Category
from app.models.question import Question
from app.schemas.practice import (
    PracticeCategoryDetail,
    PracticeCategorySummary,
    PracticeQuestion,
    PracticeQuestionOption,
)

router = APIRouter(prefix="/practice", tags=["practice"])


def _normalized_difficulty(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    trimmed = value.strip()
    if not trimmed:
        return None
    lowered = trimmed.lower()
    mapping = {
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
    }
    return mapping.get(lowered, trimmed)


def _difficulty_label(difficulties: Sequence[str]) -> str:
    unique = {_normalized_difficulty(difficulty) for difficulty in difficulties if difficulty}
    unique.discard(None)
    if not unique:
        return "Mixed"
    if len(unique) == 1:
        return next(iter(unique)) or "Mixed"
    return "Mixed"


@router.get("/categories", response_model=List[PracticeCategorySummary])
def list_practice_categories(
    db: Session = Depends(get_db_session),
) -> List[PracticeCategorySummary]:
    categories = list(
        db.scalars(
            select(Category).order_by(Category.name.asc())
        )
    )

    question_rows = db.execute(
        select(Question.category_id, Question.difficulty)
        .where(Question.is_active.is_(True))
    ).all()

    totals: Dict[int, int] = {}
    difficulties_map: Dict[int, Set[str]] = {}

    for category_id, difficulty in question_rows:
        if category_id is None:
            continue
        totals[category_id] = totals.get(category_id, 0) + 1
        normalized = _normalized_difficulty(difficulty)
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
                difficulty=_difficulty_label(difficulties),
                difficulties=difficulties,
            )
        )

    return summaries


@router.get("/categories/{slug}", response_model=PracticeCategoryDetail)
def get_practice_category(
    slug: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_session),
) -> PracticeCategoryDetail:
    category = db.scalar(select(Category).where(Category.slug == slug))
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

    questions = list(db.scalars(stmt))
    if not questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

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
        for normalized in [_normalized_difficulty(question.difficulty)]
        if normalized
    ]
    return PracticeCategoryDetail(
        slug=category.slug,
        name=category.name,
        description=category.description,
        icon=category.icon,
        total_questions=len(questions),
        difficulty=_difficulty_label(difficulties),
        questions=questions_payload,
    )

