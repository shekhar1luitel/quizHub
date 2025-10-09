from __future__ import annotations

from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.difficulty import difficulty_label, normalized_difficulty
from app.api.deps import get_current_user, get_db_session
from app.models.attempt import Attempt, AttemptAnswer
from app.models.category import Category
from app.models.question import Question, QuizQuestion
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.attempt import (
    AttemptAnswerOption,
    AttemptAnswerReview,
    AttemptCreate,
    AttemptHistoryEntry,
    AttemptResult,
)

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.post("/", response_model=AttemptResult, status_code=status.HTTP_201_CREATED)
def submit_attempt(
    payload: AttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AttemptResult:
    quiz = (
        db.query(Quiz)
        .options(
            selectinload(Quiz.questions)
            .selectinload(QuizQuestion.question)
            .selectinload(Question.options)
        )
        .filter(Quiz.id == payload.quiz_id, Quiz.is_active.is_(True))
        .first()
    )
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    questions = [link.question for link in sorted(quiz.questions, key=lambda q: q.position) if link.question]
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz has no questions")

    question_map = {question.id: question for question in questions if question.is_active}
    if not question_map:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz has no active questions")

    answer_map = {answer.question_id: answer for answer in payload.answers}
    missing_answers = [qid for qid in question_map if qid not in answer_map]
    if missing_answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing answers for questions: {missing_answers}",
        )
    invalid_question_ids = [qid for qid in answer_map if qid not in question_map]
    if invalid_question_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid questions in payload: {invalid_question_ids}",
        )

    now = datetime.now(timezone.utc)
    started_at = payload.started_at or now
    submitted_at = now
    if submitted_at < started_at:
        started_at = submitted_at
    duration_seconds = payload.duration_seconds
    if duration_seconds is None:
        duration_seconds = int((submitted_at - started_at).total_seconds())
        duration_seconds = max(duration_seconds, 0)

    attempt = Attempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        started_at=started_at,
        submitted_at=submitted_at,
        duration_seconds=duration_seconds,
        total_questions=len(question_map),
        correct_answers=0,
        score=0,
    )
    db.add(attempt)
    db.flush()

    answers: List[AttemptAnswerReview] = []
    correct_answers = 0

    for question in question_map.values():
        option_map = {option.id: option for option in question.options}
        selected = answer_map[question.id].selected_option_id
        if selected is not None and selected not in option_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid option for question {question.id}",
            )
        correct_option = next((opt for opt in question.options if opt.is_correct), None)
        is_correct = selected is not None and correct_option is not None and selected == correct_option.id
        if is_correct:
            correct_answers += 1

        db.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_option_id=selected,
                is_correct=is_correct,
            )
        )

        answers.append(
            AttemptAnswerReview(
                question_id=question.id,
                prompt=question.prompt,
                explanation=question.explanation,
                selected_option_id=selected,
                correct_option_id=correct_option.id if correct_option else None,
                is_correct=is_correct,
                options=[
                    AttemptAnswerOption(id=option.id, text=option.text)
                    for option in question.options
                ],
            )
        )

    score = round((correct_answers / len(question_map)) * 100, 2)
    attempt.correct_answers = correct_answers
    attempt.score = score

    db.commit()
    db.refresh(attempt)

    return AttemptResult(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        quiz_title=quiz.title,
        submitted_at=attempt.submitted_at,
        total_questions=attempt.total_questions,
        correct_answers=attempt.correct_answers,
        score=float(attempt.score),
        answers=answers,
    )


@router.get("/history", response_model=List[AttemptHistoryEntry])
def list_attempt_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> List[AttemptHistoryEntry]:
    attempts: List[Attempt] = (
        db.query(Attempt)
        .options(selectinload(Attempt.quiz))
        .filter(Attempt.user_id == current_user.id)
        .order_by(Attempt.submitted_at.desc())
        .all()
    )

    if not attempts:
        return []

    attempt_ids = [attempt.id for attempt in attempts]

    answer_rows = db.execute(
        select(
            AttemptAnswer.attempt_id,
            Question.category_id,
            Question.difficulty,
        )
        .join(Question, Question.id == AttemptAnswer.question_id)
        .where(AttemptAnswer.attempt_id.in_(attempt_ids))
    ).all()

    category_counts: Dict[int, Dict[Optional[int], int]] = defaultdict(lambda: defaultdict(int))
    category_names: Dict[Tuple[int, Optional[int]], str] = {}
    difficulty_map: Dict[int, List[str]] = defaultdict(list)

    # Fetch category names in a separate query to reduce duplicates.
    if answer_rows:
        category_ids = {row.category_id for row in answer_rows if row.category_id is not None}
        if category_ids:
            category_lookup = dict(
                db.execute(
                    select(Category.id, Category.name).where(Category.id.in_(category_ids))
                ).all()
            )
        else:
            category_lookup = {}

        for row in answer_rows:
            attempt_id = row.attempt_id
            category_id = row.category_id
            category_counts[attempt_id][category_id] += 1

            if category_id is not None:
                category_name = category_lookup.get(category_id, "General Practice")
            else:
                category_name = "General Practice"
            category_names[(attempt_id, category_id)] = category_name

            normalized = normalized_difficulty(row.difficulty)
            if normalized:
                difficulty_map[attempt_id].append(normalized)

    history: List[AttemptHistoryEntry] = []
    for attempt in attempts:
        top_category_id: Optional[int] = None
        top_category_name: Optional[str] = None

        counts = category_counts.get(attempt.id)
        if counts:
            sorted_categories = sorted(
                counts.items(),
                key=lambda item: (-item[1], category_names.get((attempt.id, item[0]), "")),
            )
            top_category_id = sorted_categories[0][0]
            top_category_name = category_names.get((attempt.id, top_category_id), "General Practice")

        difficulties = difficulty_map.get(attempt.id, [])
        difficulty = difficulty_label(difficulties) if difficulties else "Mixed"

        history.append(
            AttemptHistoryEntry(
                id=attempt.id,
                quiz_id=attempt.quiz_id,
                quiz_title=attempt.quiz.title if attempt.quiz else "Untitled quiz",
                submitted_at=attempt.submitted_at,
                total_questions=attempt.total_questions,
                correct_answers=attempt.correct_answers,
                score=float(attempt.score),
                duration_seconds=attempt.duration_seconds or 0,
                category_id=top_category_id,
                category_name=top_category_name,
                difficulty=difficulty,
            )
        )

    return history


@router.get("/{attempt_id}", response_model=AttemptResult)
def get_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AttemptResult:
    attempt = (
        db.query(Attempt)
        .options(
            selectinload(Attempt.quiz),
            selectinload(Attempt.answers),
        )
        .filter(Attempt.id == attempt_id, Attempt.user_id == current_user.id)
        .first()
    )
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")

    question_ids = [answer.question_id for answer in attempt.answers]
    questions = (
        db.query(Question)
        .options(selectinload(Question.options))
        .filter(Question.id.in_(question_ids))
        .all()
    )
    question_lookup = {question.id: question for question in questions}

    reviews: List[AttemptAnswerReview] = []
    for answer in attempt.answers:
        question = question_lookup.get(answer.question_id)
        if question is None:
            continue
        correct_option = next((opt for opt in question.options if opt.is_correct), None)
        reviews.append(
            AttemptAnswerReview(
                question_id=answer.question_id,
                prompt=question.prompt,
                explanation=question.explanation,
                selected_option_id=answer.selected_option_id,
                correct_option_id=correct_option.id if correct_option else None,
                is_correct=answer.is_correct,
                options=[
                    AttemptAnswerOption(id=option.id, text=option.text)
                    for option in question.options
                ],
            )
        )

    return AttemptResult(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        quiz_title=attempt.quiz.title,
        submitted_at=attempt.submitted_at,
        total_questions=attempt.total_questions,
        correct_answers=attempt.correct_answers,
        score=float(attempt.score),
        answers=reviews,
    )
