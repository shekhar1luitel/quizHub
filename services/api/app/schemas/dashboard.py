from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AttemptSummary(BaseModel):
    id: int
    quiz_id: int
    quiz_title: str
    score: float
    submitted_at: datetime


class CategoryAccuracy(BaseModel):
    category_id: Optional[int]
    category_name: str
    attempts: int
    average_score: float


class WeeklyActivityEntry(BaseModel):
    label: str
    attempts: int


class DashboardSummary(BaseModel):
    total_attempts: int
    average_score: float
    total_correct_answers: int
    total_questions_answered: int
    recent_attempts: List[AttemptSummary]
    streak: int
    category_accuracy: List[CategoryAccuracy]
    weekly_activity: List[WeeklyActivityEntry]
