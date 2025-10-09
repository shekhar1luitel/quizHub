from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Notification
from app.models.user import User


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        type: str,
        title: str,
        body: str,
        meta: dict | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            meta_json=meta or {},
        )
        self.db.add(notification)
        self.db.flush()
        return notification

    def create_many(
        self,
        user_ids: Sequence[int],
        *,
        type: str,
        title: str,
        body: str,
        meta: dict | None = None,
    ) -> int:
        if not user_ids:
            return 0
        payload = []
        meta_json = meta or {}
        for user_id in user_ids:
            payload.append(
                Notification(
                    user_id=user_id,
                    type=type,
                    title=title,
                    body=body,
                    meta_json=meta_json,
                )
            )
        self.db.add_all(payload)
        self.db.flush()
        return len(payload)

    def create_for_organization(
        self,
        organization_id: int,
        *,
        type: str,
        title: str,
        body: str,
        meta: dict | None = None,
    ) -> int:
        stmt = (
            select(User.id)
            .where(User.organization_id == organization_id)
            .where(User.status == "active")
        )
        user_ids = self.db.scalars(stmt).all()
        return self.create_many(
            user_ids,
            type=type,
            title=title,
            body=body,
            meta=meta,
        )

    def list_for_user(
        self,
        user_id: int,
        *,
        limit: int = 20,
        cursor: datetime | None = None,
        unread_only: bool = False,
    ) -> tuple[List[Notification], datetime | None]:
        limit = max(1, min(limit, 100))
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.read_at.is_(None))
        if cursor is not None:
            stmt = stmt.where(Notification.created_at < cursor)
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit + 1)
        rows = self.db.scalars(stmt).all()
        next_cursor = None
        if len(rows) > limit:
            next_cursor = rows[-1].created_at
            rows = rows[:limit]
        return rows, next_cursor

    def mark_read(self, notification_id: int, user_id: int) -> bool:
        stmt = (
            select(Notification)
            .where(Notification.id == notification_id)
            .where(Notification.user_id == user_id)
            .limit(1)
        )
        notification = self.db.scalar(stmt)
        if not notification:
            return False
        if notification.read_at is None:
            notification.read_at = datetime.now(timezone.utc)
            self.db.add(notification)
        return True

    def mark_all_read(self, user_id: int) -> int:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.read_at.is_(None))
        )
        notifications = self.db.scalars(stmt).all()
        updated = 0
        now = datetime.now(timezone.utc)
        for notification in notifications:
            notification.read_at = now
            updated += 1
        return updated


def get_notification_service(db: Session) -> NotificationService:
    return NotificationService(db)
