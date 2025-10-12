from __future__ import annotations

from typing import List, Sequence

from typing import List, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import (
    get_db_session,
    resolve_content_organization,
    require_content_manager,
)
from app.models.category import Category
from app.models.question import Option, Question
from app.models.topic import Topic
from app.models.user import User
from app.schemas.question import OptionCreate, QuestionCreate, QuestionOut, QuestionSummary, QuestionUpdate

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=List[QuestionSummary])
def list_questions(
    organization_id: int | None = Query(default=None),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
) -> List[QuestionSummary]:
    if organization_id is not None:
        target_org_id = resolve_content_organization(
            current_user,
            organization_id,
            allow_global_for_admin=True,
        )
    elif current_user.role == "org_admin":
        if current_user.organization_id is None:
            return []
        target_org_id = current_user.organization_id
    elif current_user.role == "admin":
        target_org_id = None
    else:
        target_org_id = None
    stmt = (
        select(
            Question.id,
            Question.prompt,
            Question.subject,
            Question.difficulty,
            Question.is_active,
            Question.category_id,
            Question.organization_id,
            Category.name.label("category_name"),
            Question.topic_id,
            Topic.name.label("topic_name"),
            func.count(Option.id).label("option_count"),
        )
        .join(Category, Category.id == Question.category_id)
        .join(Option, Option.question_id == Question.id)
        .join(Topic, Topic.id == Question.topic_id, isouter=True)
        .group_by(
            Question.id,
            Question.prompt,
            Question.subject,
            Question.difficulty,
            Question.is_active,
            Question.category_id,
            Question.organization_id,
            Category.name,
            Question.topic_id,
            Topic.name,
        )
        .order_by(Question.id.desc())
    )
    if target_org_id is not None:
        stmt = stmt.where(Question.organization_id == target_org_id)
    elif current_user.role == "admin":
        stmt = stmt.where(Question.organization_id.is_(None))
    elif current_user.role != "superuser":
        return []
    rows = db.execute(stmt).all()
    return [
        QuestionSummary(
            id=row.id,
            prompt=row.prompt,
            subject=row.subject,
            difficulty=row.difficulty,
            is_active=row.is_active,
            option_count=row.option_count,
            category_id=row.category_id,
            category_name=row.category_name,
            organization_id=row.organization_id,
            topic_id=row.topic_id,
            topic_name=row.topic_name,
        )
        for row in rows
    ]


@router.get("/{question_id}", response_model=QuestionOut)
def get_question(
    question_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> QuestionOut:
    question = (
        db.query(Question)
        .options(
            selectinload(Question.options),
            selectinload(Question.category),
            selectinload(Question._topic),
        )
        .filter(Question.id == question_id)
        .first()
    )
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    target_org_id = resolve_content_organization(
        current_user,
        organization_id if organization_id is not None else question.organization_id,
        allow_global_for_admin=True,
    )
    if target_org_id is not None:
        if question.organization_id != target_org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Question belongs to another organization")
    elif current_user.role != "superuser" and question.organization_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Question belongs to another organization")
    return QuestionOut.model_validate(question)


def _ensure_topic_for_subject(
    db: Session,
    topic_id: int | None,
    subject_id: int,
) -> Topic | None:
    if topic_id is None:
        return None
    topic = db.get(Topic, topic_id)
    if topic is None or topic.subject_id != subject_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected topic does not belong to the subject.",
        )
    return topic


@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> QuestionOut:
    validate_options(payload.options)
    target_org_id = resolve_content_organization(
        current_user,
        organization_id,
        allow_global_for_admin=True,
    )
    category = _ensure_category_exists(db, payload.category_id, target_org_id, current_user)
    topic = _ensure_topic_for_subject(db, payload.topic_id, category.id)

    question = Question(
        prompt=payload.prompt,
        explanation=payload.explanation,
        subject=payload.subject,
        difficulty=payload.difficulty,
        is_active=payload.is_active,
        category_id=payload.category_id,
        topic_id=topic.id if topic is not None else None,
        organization_id=target_org_id if target_org_id is not None else category.organization_id,
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
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> QuestionOut:
    question = (
        db.query(Question)
        .options(selectinload(Question.options), selectinload(Question.category))
        .filter(Question.id == question_id)
        .first()
    )
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    target_org_id = resolve_content_organization(
        current_user,
        organization_id if organization_id is not None else question.organization_id,
        allow_global_for_admin=True,
    )
    if target_org_id is not None:
        if question.organization_id != target_org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Question belongs to another organization")
    elif current_user.role != "superuser" and question.organization_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Question belongs to another organization")

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
    if payload.category_id is not None:
        category = _ensure_category_exists(db, payload.category_id, target_org_id, current_user)
        question.category_id = payload.category_id
        question.organization_id = target_org_id if target_org_id is not None else category.organization_id
        if question.topic_id is not None:
            current_topic = db.get(Topic, question.topic_id)
            if current_topic is None or current_topic.subject_id != question.category_id:
                question.topic_id = None

    if "topic_id" in payload.model_fields_set:
        if payload.topic_id is None:
            question.topic_id = None
        else:
            topic = _ensure_topic_for_subject(db, payload.topic_id, question.category_id)
            question.topic_id = topic.id

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
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> None:
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    target_org_id = resolve_content_organization(
        current_user,
        organization_id if organization_id is not None else question.organization_id,
        allow_global_for_admin=True,
    )
    if target_org_id is not None:
        if question.organization_id != target_org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Question belongs to another organization")
    elif current_user.role != "superuser" and question.organization_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Question belongs to another organization")
    db.delete(question)
    db.commit()


def validate_options(options: Sequence[OptionCreate]) -> None:
    if len(options) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Add at least two options")
    if not any(option.is_correct for option in options):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mark one option as correct")


def _ensure_category_exists(
    db: Session,
    category_id: int,
    target_org_id: int | None,
    current_user: User,
) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if target_org_id is not None:
        if category.organization_id != target_org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Category belongs to another organization")
    elif current_user.role != "superuser" and category.organization_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Category belongs to another organization")
    return category
