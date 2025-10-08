from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin
from app.core.strings import slugify
from app.models.category import Category
from app.models.question import Question
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


@router.get("/", response_model=List[CategoryOut])
def list_categories(
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> List[CategoryOut]:
    categories = list(db.scalars(select(Category).order_by(Category.name.asc())))
    return [CategoryOut.model_validate(category) for category in categories]


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> CategoryOut:
    name = payload.name.strip()
    slug = slugify(name)

    existing = db.scalar(select(Category).where(Category.slug == slug))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A category with this name already exists.",
        )

    category = Category(
        name=name,
        slug=slug,
        description=_normalize_optional(payload.description),
        icon=_normalize_optional(payload.icon),
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return CategoryOut.model_validate(category)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> CategoryOut:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if payload.name is not None:
        new_name = payload.name.strip()
        if not new_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name cannot be empty.",
            )
        new_slug = slugify(new_name)
        duplicate = db.scalar(
            select(Category).where(Category.slug == new_slug, Category.id != category.id)
        )
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another category with this name already exists.",
            )
        category.name = new_name
        category.slug = new_slug

    if payload.description is not None:
        category.description = _normalize_optional(payload.description)
    if payload.icon is not None:
        category.icon = _normalize_optional(payload.icon)

    db.commit()
    db.refresh(category)
    return CategoryOut.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db_session),
    _: None = Depends(require_admin),
) -> None:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    question_count = db.scalar(
        select(func.count()).select_from(Question).where(Question.category_id == category.id)
    )
    if question_count and question_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Remove or reassign questions before deleting this category.",
        )

    db.delete(category)
    db.commit()
