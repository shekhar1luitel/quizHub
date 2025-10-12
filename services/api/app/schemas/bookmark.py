from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookmarkCreate(BaseModel):
    question_id: int


class BookmarkOut(BaseModel):
    id: int
    question_id: int
    created_at: datetime
    prompt: str
    subject: str | None
    difficulty: str | None
    subject_id: int
    subject_name: str

    model_config = ConfigDict(from_attributes=True)
