from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db_session
from app.models.bookmark import Bookmark
from app.models.category import Category
from app.models.question import Question
from app.models.topic import Topic
from app.models.user import User
from app.schemas.bookmark import BookmarkCreate, BookmarkOut

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


def _bookmark_to_out(
    bookmark: Bookmark, question: Question, category: Category, topic: Topic | None
) -> BookmarkOut:
    return BookmarkOut(
        id=bookmark.id,
        question_id=bookmark.question_id,
        created_at=bookmark.created_at,
        prompt=question.prompt,
        subject=question.subject,
        difficulty=question.difficulty,
        category_id=category.id,
        category_name=category.name,
        topic_id=topic.id if topic is not None else None,
        topic_name=topic.name if topic is not None else None,
    )


@router.get("/", response_model=List[BookmarkOut])
def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> List[BookmarkOut]:
    stmt = (
        select(Bookmark)
        .options(
            joinedload(Bookmark.question)
            .joinedload(Question.category),
            joinedload(Bookmark.question).joinedload(Question._topic),
        )
        .where(Bookmark.user_id == current_user.id)
        .order_by(Bookmark.created_at.desc())
    )
    bookmarks = db.scalars(stmt).all()
    results: List[BookmarkOut] = []
    for bookmark in bookmarks:
        question = bookmark.question
        category = question.category
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bookmark is missing category information",
            )
        results.append(_bookmark_to_out(bookmark, question, category, question.topic))
    return results


@router.get("/ids", response_model=List[int])
def list_bookmarked_question_ids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> List[int]:
    stmt = select(Bookmark.question_id).where(Bookmark.user_id == current_user.id)
    return [row[0] for row in db.execute(stmt)]


@router.post("/", response_model=BookmarkOut, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    payload: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> BookmarkOut:
    question = (
        db.query(Question)
        .options(joinedload(Question.category), joinedload(Question._topic))
        .filter(Question.id == payload.question_id)
        .first()
    )
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    if question.category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is missing category",
        )

    bookmark = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id, Bookmark.question_id == question.id)
        .first()
    )
    if bookmark is None:
        bookmark = Bookmark(user_id=current_user.id, question_id=question.id)
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
    else:
        db.refresh(bookmark)

    return _bookmark_to_out(bookmark, question, question.category, question.topic)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    bookmark = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id, Bookmark.question_id == question_id)
        .first()
    )
    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
