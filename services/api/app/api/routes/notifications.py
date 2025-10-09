from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.schemas.notifications import NotificationListResponse, NotificationReadResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    unread: int | None = Query(default=None, ge=0, le=1),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: datetime | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    service = NotificationService(db)
    notifications, next_cursor = service.list_for_user(
        current_user.id,
        limit=limit,
        cursor=cursor,
        unread_only=bool(unread),
    )
    return NotificationListResponse.from_entities(notifications, next_cursor)


@router.post("/{notification_id}/read", response_model=NotificationReadResponse)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    service = NotificationService(db)
    success = service.mark_read(notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    db.commit()
    return NotificationReadResponse(marked=True)


@router.post("/read-all", response_model=NotificationReadResponse)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    service = NotificationService(db)
    updated = service.mark_all_read(current_user.id)
    db.commit()
    return NotificationReadResponse(marked=bool(updated), count=updated)
