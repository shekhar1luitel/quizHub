from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import (
    get_db_session,
    resolve_content_organization,
    require_content_manager,
)
from app.core.strings import slugify
from app.models.category import Category
from app.models.question import Question
from app.models.topic import Topic
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectOut, SubjectUpdate
from app.schemas.topic import TopicCreate, TopicOut, TopicUpdate

router = APIRouter(prefix="/subjects", tags=["subjects"])


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


def _resolve_subject(
    db: Session,
    subject_id: int,
    current_user: User,
    organization_id: int | None,
) -> Category:
    subject = db.get(Category, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    target_org_id = resolve_content_organization(
        current_user,
        organization_id if organization_id is not None else subject.organization_id,
        allow_global_for_admin=True,
    )

    if target_org_id is not None:
        if subject.organization_id != target_org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Subject belongs to another organization")
    elif current_user.role != "superuser" and subject.organization_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Subject belongs to another organization")

    return subject


@router.get("/", response_model=List[SubjectOut])
def list_subjects(
    organization_id: int | None = Query(default=None),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
) -> List[SubjectOut]:
    stmt = select(Category).options(selectinload(Category.topics)).order_by(Category.name.asc())

    if organization_id is not None:
        target_org_id = resolve_content_organization(
            current_user,
            organization_id,
            allow_global_for_admin=True,
        )
        if target_org_id is not None:
            stmt = stmt.where(Category.organization_id == target_org_id)
        else:
            stmt = stmt.where(Category.organization_id.is_(None))
    elif current_user.role == "org_admin":
        org_id = current_user.organization_id
        if org_id is None:
            return []
        stmt = stmt.where(Category.organization_id == org_id)
    elif current_user.role == "admin":
        stmt = stmt.where(Category.organization_id.is_(None))

    subjects = list(db.scalars(stmt))
    return [SubjectOut.model_validate(subject) for subject in subjects]


@router.post("/", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(
    payload: SubjectCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> SubjectOut:
    name = payload.name.strip()
    slug = slugify(name)
    target_org_id = resolve_content_organization(
        current_user,
        organization_id,
        allow_global_for_admin=True,
    )

    existing = db.scalar(
        select(Category).where(
            Category.slug == slug,
            Category.organization_id == target_org_id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A subject with this name already exists.",
        )

    subject = Category(
        name=name,
        slug=slug,
        description=_normalize_optional(payload.description),
        icon=_normalize_optional(payload.icon),
        organization_id=target_org_id,
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return SubjectOut.model_validate(subject)


@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> SubjectOut:
    subject = _resolve_subject(db, subject_id, current_user, organization_id)

    target_org_id = resolve_content_organization(
        current_user,
        organization_id if organization_id is not None else subject.organization_id,
        allow_global_for_admin=True,
    )

    if payload.name is not None:
        new_name = payload.name.strip()
        if not new_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name cannot be empty.",
            )
        new_slug = slugify(new_name)
        duplicate = db.scalar(
            select(Category).where(
                Category.slug == new_slug,
                Category.id != subject.id,
                Category.organization_id == target_org_id,
            )
        )
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another subject with this name already exists.",
            )
        subject.name = new_name
        subject.slug = new_slug

    if payload.description is not None:
        subject.description = _normalize_optional(payload.description)
    if payload.icon is not None:
        subject.icon = _normalize_optional(payload.icon)
    if current_user.role == "org_admin" or organization_id is not None:
        subject.organization_id = target_org_id

    db.commit()
    db.refresh(subject)
    return SubjectOut.model_validate(subject)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> None:
    subject = _resolve_subject(db, subject_id, current_user, organization_id)

    question_count = db.scalar(
        select(func.count()).select_from(Question).where(Question.category_id == subject.id)
    )
    if question_count and question_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Remove or reassign questions before deleting this subject.",
        )

    db.delete(subject)
    db.commit()


@router.get("/{subject_id}/topics", response_model=List[TopicOut])
def list_topics(
    subject_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> List[TopicOut]:
    subject = _resolve_subject(db, subject_id, current_user, organization_id)
    return [TopicOut.model_validate(topic) for topic in subject.topics]


@router.post("/{subject_id}/topics", response_model=TopicOut, status_code=status.HTTP_201_CREATED)
def create_topic(
    subject_id: int,
    payload: TopicCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> TopicOut:
    subject = _resolve_subject(db, subject_id, current_user, organization_id)

    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name cannot be empty.")
    slug = slugify(name)

    duplicate = db.scalar(
        select(Topic).where(
            Topic.subject_id == subject.id,
            Topic.slug == slug,
        )
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A topic with this name already exists for this subject.",
        )

    topic = Topic(
        subject_id=subject.id,
        name=name,
        slug=slug,
        description=_normalize_optional(payload.description),
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return TopicOut.model_validate(topic)


@router.put("/{subject_id}/topics/{topic_id}", response_model=TopicOut)
def update_topic(
    subject_id: int,
    topic_id: int,
    payload: TopicUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> TopicOut:
    subject = _resolve_subject(db, subject_id, current_user, organization_id)
    topic = db.get(Topic, topic_id)
    if topic is None or topic.subject_id != subject.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    if payload.name is not None:
        new_name = payload.name.strip()
        if not new_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name cannot be empty.",
            )
        new_slug = slugify(new_name)
        duplicate = db.scalar(
            select(Topic).where(
                Topic.subject_id == subject.id,
                Topic.slug == new_slug,
                Topic.id != topic.id,
            )
        )
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another topic with this name already exists.",
            )
        topic.name = new_name
        topic.slug = new_slug

    if payload.description is not None:
        topic.description = _normalize_optional(payload.description)

    db.commit()
    db.refresh(topic)
    return TopicOut.model_validate(topic)


@router.delete("/{subject_id}/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    subject_id: int,
    topic_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
    organization_id: int | None = Query(default=None),
) -> None:
    subject = _resolve_subject(db, subject_id, current_user, organization_id)
    topic = db.get(Topic, topic_id)
    if topic is None or topic.subject_id != subject.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    question_count = db.scalar(
        select(func.count()).select_from(Question).where(Question.topic_id == topic.id)
    )
    if question_count and question_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Remove or reassign questions before deleting this topic.",
        )

    db.delete(topic)
    db.commit()
