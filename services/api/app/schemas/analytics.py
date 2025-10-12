from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class OverallStats(BaseModel):
    total_tests: int
    average_score: float
    total_time_spent_seconds: int
    improvement_rate: float
    streak: int


class SubjectPerformance(BaseModel):
    subject: str
    tests: int
    average_score: float
    best_score: float
    improvement: float


class WeeklyProgressEntry(BaseModel):
    label: str
    tests: int
    average_score: float


class TimeAnalysis(BaseModel):
    average_time_per_question_seconds: float
    fastest_attempt_seconds: int
    slowest_attempt_seconds: int
    recommended_time_per_question_lower: float
    recommended_time_per_question_upper: float


class AnalyticsOverview(BaseModel):
    generated_at: datetime
    overall_stats: OverallStats
    subject_performance: List[SubjectPerformance]
    weekly_progress: List[WeeklyProgressEntry]
    time_analysis: Optional[TimeAnalysis]
    strengths: List[str]
    weaknesses: List[str]
