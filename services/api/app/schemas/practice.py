from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class PracticeCategorySummary(BaseModel):
    slug: str
    name: str
    total_questions: int
    difficulty: str
    difficulties: List[str]


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
    total_questions: int
    difficulty: str
    questions: List[PracticeQuestion]

