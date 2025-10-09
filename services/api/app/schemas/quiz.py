from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class QuizBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    is_active: bool = True


class QuizCreate(QuizBase):
    question_ids: List[int] = Field(default_factory=list)
    organization_id: Optional[int] = None


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    question_ids: Optional[List[int]] = None
    organization_id: Optional[int] = None


class QuizSummary(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_active: bool
    question_count: int
    organization_id: Optional[int]

    model_config = {
        "from_attributes": True,
    }


class QuizQuestionOption(BaseModel):
    id: int
    text: str

    model_config = {
        "from_attributes": True,
    }


class QuizQuestion(BaseModel):
    id: int
    prompt: str
    subject: Optional[str]
    difficulty: Optional[str]
    options: List[QuizQuestionOption]

    model_config = {
        "from_attributes": True,
    }


class QuizDetail(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_active: bool
    questions: List[QuizQuestion]
    organization_id: Optional[int]

    model_config = {
        "from_attributes": True,
    }
