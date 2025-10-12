from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.topic import TopicOut

class PublicCategorySummary(BaseModel):
    slug: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    total_questions: int
    difficulty: str
    topics: List[TopicOut] = []


class PublicQuizSummary(BaseModel):
    id: int
    title: str
    description: Optional[str]
    question_count: int
    total_attempts: int
    created_at: datetime


class PublicHomeResponse(BaseModel):
    featured_categories: List[PublicCategorySummary]
    trending_quizzes: List[PublicQuizSummary]
