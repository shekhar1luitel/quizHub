from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class AdminTotals(BaseModel):
    total_quizzes: int
    active_quizzes: int
    total_questions: int
    inactive_questions: int
    total_categories: int
    total_users: int


class AdminRecentQuiz(BaseModel):
    id: int
    title: str
    question_count: int
    is_active: bool
    created_at: datetime


class AdminCategorySnapshot(BaseModel):
    id: int
    name: str
    question_count: int


class AdminOverview(BaseModel):
    totals: AdminTotals
    recent_quizzes: List[AdminRecentQuiz]
    top_categories: List[AdminCategorySnapshot]
