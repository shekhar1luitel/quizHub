from __future__ import annotations

from typing import List, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin
from app.models.question import Option, Question
from app.schemas.question import OptionCreate, QuestionCreate, QuestionOut, QuestionSummary, QuestionUpdate

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=List[QuestionSummary])
def list_questions(
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> List[QuestionSummary]:
    stmt = (
        select(
            Question.id,
            Question.prompt,
            Question.subject,
            Question.difficulty,
            Question.is_active,
            func.count(Option.id).label("option_count"),
        )
        .join(Option, Option.question_id == Question.id)
        .group_by(Question.id)
        .order_by(Question.id.desc())
    )
    rows = db.execute(stmt).all()
    return [
        QuestionSummary(
            id=row.id,
            prompt=row.prompt,
            subject=row.subject,
            difficulty=row.difficulty,
            is_active=row.is_active,
            option_count=row.option_count,
        )
        for row in rows
    ]


@router.get("/{question_id}", response_model=QuestionOut)
def get_question(
    question_id: int,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> QuestionOut:
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return QuestionOut.model_validate(question)


@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> QuestionOut:
    validate_options(payload.options)

    question = Question(
        prompt=payload.prompt,
        explanation=payload.explanation,
        subject=payload.subject,
        difficulty=payload.difficulty,
        is_active=payload.is_active,
    )
    db.add(question)
    db.flush()

    for option in payload.options:
        db.add(Option(question_id=question.id, text=option.text, is_correct=option.is_correct))

    db.commit()
    db.refresh(question)
    return QuestionOut.model_validate(question)


@router.put("/{question_id}", response_model=QuestionOut)
def update_question(
    question_id: int,
    payload: QuestionUpdate,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> QuestionOut:
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    if payload.prompt is not None:
        question.prompt = payload.prompt
    if payload.explanation is not None:
        question.explanation = payload.explanation
    if payload.subject is not None:
        question.subject = payload.subject
    if payload.difficulty is not None:
        question.difficulty = payload.difficulty
    if payload.is_active is not None:
        question.is_active = payload.is_active

    if payload.options is not None:
        validate_options(payload.options)
        db.query(Option).filter(Option.question_id == question.id).delete(synchronize_session=False)
        for option in payload.options:
            db.add(Option(question_id=question.id, text=option.text, is_correct=option.is_correct))

    db.commit()
    db.refresh(question)
    return QuestionOut.model_validate(question)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> None:
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    db.delete(question)
    db.commit()


def validate_options(options: Sequence[OptionCreate]) -> None:
    if len(options) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Add at least two options")
    if not any(option.is_correct for option in options):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mark one option as correct")
