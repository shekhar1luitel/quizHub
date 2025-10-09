from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.category import CategorySummary


class OptionBase(BaseModel):
    text: str = Field(..., min_length=1)
    is_correct: bool = False


class OptionCreate(OptionBase):
    pass


class OptionOut(OptionBase):
    id: int

    model_config = {
        "from_attributes": True,
    }


class QuestionBase(BaseModel):
    prompt: str = Field(..., min_length=1)
    explanation: Optional[str] = None
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    is_active: bool = True
    category_id: int
    organization_id: Optional[int] = None


class QuestionCreate(QuestionBase):
    options: List[OptionCreate]


class QuestionUpdate(BaseModel):
    prompt: Optional[str] = Field(None, min_length=1)
    explanation: Optional[str] = None
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    is_active: Optional[bool] = None
    options: Optional[List[OptionCreate]] = None
    category_id: Optional[int] = None


class QuestionOut(QuestionBase):
    id: int
    category: CategorySummary
    options: List[OptionOut]

    model_config = {
        "from_attributes": True,
    }


class QuestionSummary(BaseModel):
    id: int
    prompt: str
    subject: Optional[str]
    difficulty: Optional[str]
    is_active: bool
    option_count: int
    category_id: int
    category_name: str
    organization_id: Optional[int]

    model_config = {
        "from_attributes": True,
    }
