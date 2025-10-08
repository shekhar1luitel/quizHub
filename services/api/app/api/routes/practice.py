from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Sequence, Set

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db_session
from app.models.question import Question
from app.schemas.practice import (
    PracticeCategoryDetail,
    PracticeCategorySummary,
    PracticeQuestion,
    PracticeQuestionOption,
)

router = APIRouter(prefix="/practice", tags=["practice"])


def _normalized_subject(subject: Optional[str]) -> Optional[str]:
    if subject is None:
        return None
    cleaned = subject.strip()
    return cleaned or None


def _subject_display_name(subject: Optional[str]) -> str:
    return _normalized_subject(subject) or "General"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "general"


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


def _collect_category_metadata(db: Session) -> Dict[str, Dict[str, object]]:
    stmt = (
        select(Question.subject, Question.difficulty, func.count(Question.id))
        .where(Question.is_active.is_(True))
        .group_by(Question.subject, Question.difficulty)
    )
    metadata: Dict[str, Dict[str, object]] = {}
    for subject, difficulty, count in db.execute(stmt):
        name = _subject_display_name(subject)
        slug = _slugify(name)
        entry = metadata.setdefault(
            slug,
            {
                "name": name,
                "total": 0,
                "difficulties": set(),
                "subjects": set(),
            },
        )
        entry["total"] = int(entry["total"]) + int(count)
        entry["subjects"].add(_normalized_subject(subject))
        normalized_difficulty = _normalized_difficulty(difficulty)
        if normalized_difficulty:
            entry["difficulties"].add(normalized_difficulty)
    return metadata


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
    metadata = _collect_category_metadata(db)
    summaries: List[PracticeCategorySummary] = []
    for slug, info in metadata.items():
        difficulties = sorted(info["difficulties"])  # type: ignore[arg-type]
        summaries.append(
            PracticeCategorySummary(
                slug=slug,
                name=info["name"],  # type: ignore[arg-type]
                total_questions=info["total"],  # type: ignore[arg-type]
                difficulty=_difficulty_label(difficulties),
                difficulties=difficulties,
            )
        )
    summaries.sort(key=lambda item: item.name.lower())
    return summaries


def _subject_filters(subjects: Iterable[Optional[str]]):
    normalized: Set[Optional[str]] = { _normalized_subject(subject) for subject in subjects }
    string_subjects = sorted({subject for subject in normalized if subject})
    include_empty = None in normalized

    conditions = []
    if string_subjects:
        conditions.append(Question.subject.in_(string_subjects))
    if include_empty:
        conditions.append(Question.subject.is_(None))
        conditions.append(Question.subject == "")
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return or_(*conditions)


@router.get("/categories/{slug}", response_model=PracticeCategoryDetail)
def get_practice_category(
    slug: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_session),
) -> PracticeCategoryDetail:
    metadata = _collect_category_metadata(db)
    info = metadata.get(slug)
    if info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    filters = _subject_filters(info["subjects"])  # type: ignore[arg-type]
    if filters is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    stmt = (
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.is_active.is_(True))
        .where(filters)
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
        slug=slug,
        name=info["name"],  # type: ignore[arg-type]
        total_questions=info["total"],  # type: ignore[arg-type]
        difficulty=_difficulty_label(difficulties),
        questions=questions_payload,
    )

