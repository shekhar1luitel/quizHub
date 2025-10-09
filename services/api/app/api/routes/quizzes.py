from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user_optional, get_db_session, require_admin
from app.models.question import Question, QuizQuestion
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.quiz import (
    QuizCreate,
    QuizDetail,
    QuizQuestion as QuizQuestionSchema,
    QuizQuestionOption,
    QuizSummary,
    QuizUpdate,
)

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("/", response_model=List[QuizSummary])
def list_quizzes(db: Session = Depends(get_db_session)) -> List[QuizSummary]:
    stmt = (
        select(
            Quiz.id,
            Quiz.title,
            Quiz.description,
            Quiz.is_active,
            func.count(QuizQuestion.question_id).label("question_count"),
        )
        .join(QuizQuestion, QuizQuestion.quiz_id == Quiz.id, isouter=True)
        .group_by(Quiz.id)
        .order_by(Quiz.title)
    )
    rows = db.execute(stmt).all()
    return [
        QuizSummary(
            id=row.id,
            title=row.title,
            description=row.description,
            is_active=row.is_active,
            question_count=row.question_count,
        )
        for row in rows
    ]


@router.get("/{quiz_id}", response_model=QuizDetail)
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db_session),
    current_user: User | None = Depends(get_current_user_optional),
) -> QuizDetail:
    quiz = (
        db.query(Quiz)
        .options(
            selectinload(Quiz.questions)
            .selectinload(QuizQuestion.question)
            .selectinload(Question.options)
        )
        .filter(Quiz.id == quiz_id)
        .first()
    )
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    if not quiz.is_active:
        if current_user is None or current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    questions: List[QuizQuestionSchema] = []
    for link in sorted(quiz.questions, key=lambda q: q.position):
        question = link.question
        if question is None:
            continue
        if not question.is_active and (current_user is None or current_user.role != "admin"):
            continue
        questions.append(
            QuizQuestionSchema(
                id=question.id,
                prompt=question.prompt,
                subject=question.subject,
                difficulty=question.difficulty,
                options=[
                    QuizQuestionOption(id=option.id, text=option.text) for option in question.options
                ],
            )
        )

    return QuizDetail(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        is_active=quiz.is_active,
        questions=questions,
    )


@router.post("/", response_model=QuizSummary, status_code=status.HTTP_201_CREATED)
def create_quiz(
    payload: QuizCreate,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> QuizSummary:
    if db.query(Quiz).filter(Quiz.title == payload.title).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz title already exists")

    quiz = Quiz(title=payload.title, description=payload.description, is_active=payload.is_active)
    db.add(quiz)
    db.flush()

    attach_questions(payload.question_ids, quiz, db)

    db.commit()
    db.refresh(quiz)

    question_count = len(payload.question_ids)
    return QuizSummary(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        is_active=quiz.is_active,
        question_count=question_count,
    )


@router.put("/{quiz_id}", response_model=QuizSummary)
def update_quiz(
    quiz_id: int,
    payload: QuizUpdate,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> QuizSummary:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    if payload.title is not None:
        existing = (
            db.query(Quiz)
            .filter(Quiz.title == payload.title, Quiz.id != quiz_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz title already exists")
        quiz.title = payload.title

    if payload.description is not None:
        quiz.description = payload.description
    if payload.is_active is not None:
        quiz.is_active = payload.is_active

    if payload.question_ids is not None:
        quiz.questions.clear()
        db.flush()
        attach_questions(payload.question_ids, quiz, db)

    db.commit()
    db.refresh(quiz)

    question_count = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).count()
    return QuizSummary(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        is_active=quiz.is_active,
        question_count=question_count,
    )


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> None:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    db.delete(quiz)
    db.commit()


def attach_questions(question_ids: List[int], quiz: Quiz, db: Session) -> None:
    if not question_ids:
        return

    if len(set(question_ids)) != len(question_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate questions are not allowed in a quiz",
        )

    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    missing_ids = set(question_ids) - {question.id for question in questions}
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown question ids: {sorted(missing_ids)}",
        )

    for position, question_id in enumerate(question_ids, start=1):
        quiz.questions.append(QuizQuestion(quiz_id=quiz.id, question_id=question_id, position=position))
