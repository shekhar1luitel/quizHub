from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db_session,
    resolve_content_organization,
    require_content_manager,
)
from app.core.strings import slugify
from app.models.subject import Subject
from app.models.question import Question
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectOut, SubjectUpdate

router = APIRouter(prefix="/subjects", tags=["subjects"])


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


@router.get("/", response_model=List[SubjectOut])
def list_subjects(
    organization_id: int | None = Query(default=None),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_content_manager),
) -> List[SubjectOut]:
    stmt = select(Subject).order_by(Subject.name.asc())

    if organization_id is not None:
        target_org_id = resolve_content_organization(
            current_user,
            organization_id,
            allow_global_for_admin=True,
        )
        if target_org_id is not None:
            stmt = stmt.where(Subject.organization_id == target_org_id)
        else:
            stmt = stmt.where(Subject.organization_id.is_(None))
    elif current_user.role == "org_admin":
        org_id = current_user.organization_id
        if org_id is None:
            return []
        stmt = stmt.where(Subject.organization_id == org_id)
    elif current_user.role == "admin":
        stmt = stmt.where(Subject.organization_id.is_(None))

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
        select(Subject).where(
            Subject.slug == slug,
            Subject.organization_id == target_org_id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A subject with this name already exists.",
        )

    subject = Subject(
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
    subject = db.get(Subject, subject_id)
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

    if payload.name is not None:
        new_name = payload.name.strip()
        if not new_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name cannot be empty.",
            )
        new_slug = slugify(new_name)
        duplicate = db.scalar(
            select(Subject).where(
                Subject.slug == new_slug,
                Subject.id != subject.id,
                Subject.organization_id == target_org_id,
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
    subject = db.get(Subject, subject_id)
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

    question_count = db.scalar(
        select(func.count()).select_from(Question).where(Question.subject_id == subject.id)
    )
    if question_count and question_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Remove or reassign questions before deleting this subject.",
        )

    db.delete(subject)
    db.commit()
