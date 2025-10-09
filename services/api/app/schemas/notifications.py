from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.organization import Notification


class NotificationItem(BaseModel):
    id: int
    type: str
    title: str
    body: str
    meta: dict | None = Field(default=None)
    read_at: Optional[datetime]
    created_at: datetime

    @classmethod
    def from_entity(cls, notification: Notification) -> "NotificationItem":
        return cls(
            id=notification.id,
            type=notification.type,
            title=notification.title,
            body=notification.body,
            meta=notification.meta_json,
            read_at=notification.read_at,
            created_at=notification.created_at,
        )


class NotificationListResponse(BaseModel):
    items: List[NotificationItem]
    next_cursor: Optional[datetime] = None

    @classmethod
    def from_entities(
        cls, notifications: List[Notification], next_cursor: datetime | None
    ) -> "NotificationListResponse":
        return cls(
            items=[NotificationItem.from_entity(notification) for notification in notifications],
            next_cursor=next_cursor,
        )


class NotificationReadResponse(BaseModel):
    marked: bool
    count: int | None = None
