from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from app.schemas.topic import TopicOut

class PracticeCategorySummary(BaseModel):
    slug: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    total_questions: int
    difficulty: str
    difficulties: List[str]
    quiz_id: Optional[int] = None
    organization_id: Optional[int] = None
    topics: List[TopicOut] = []


class PracticeQuestionOption(BaseModel):
    id: int
    text: str
    is_correct: bool

    model_config = {
        "from_attributes": True,
    }


class PracticeQuestion(BaseModel):
    id: int
    prompt: str
    explanation: Optional[str]
    difficulty: Optional[str]
    options: List[PracticeQuestionOption]

    model_config = {
        "from_attributes": True,
    }


class PracticeCategoryDetail(BaseModel):
    slug: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    total_questions: int
    difficulty: str
    questions: List[PracticeQuestion]
    organization_id: Optional[int] = None
    topics: List[TopicOut] = []
