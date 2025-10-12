from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)


class TopicOut(TopicBase):
    id: int
    slug: str
    subject_id: int

    model_config = {"from_attributes": True}
