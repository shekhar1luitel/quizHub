from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


class BulkCategoryPreview(BaseModel):
    source_row: int | None = Field(default=None, description="Row number in the spreadsheet")
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=16)
    slug: str
    action: Literal["create", "update"]
    errors: List[str] = Field(default_factory=list)


class BulkQuizPreview(BaseModel):
    source_row: int | None = Field(default=None)
    title: str = Field(..., min_length=1)
    description: str | None = Field(default=None)
    is_active: bool = True
    question_prompts: List[str] = Field(default_factory=list)
    action: Literal["create", "update"]
    errors: List[str] = Field(default_factory=list)


class BulkQuestionOption(BaseModel):
    text: str = Field(..., min_length=1)
    is_correct: bool = False


class BulkQuestionPreview(BaseModel):
    source_row: int | None = Field(default=None)
    prompt: str = Field(..., min_length=1)
    explanation: str | None = Field(default=None)
    subject: str | None = Field(default=None)
    difficulty: str | None = Field(default=None)
    is_active: bool = True
    category_name: str = Field(..., min_length=1)
    quiz_titles: List[str] = Field(default_factory=list)
    options: List[BulkQuestionOption]
    action: Literal["create", "update"]
    errors: List[str] = Field(default_factory=list)


class BulkImportPreview(BaseModel):
    categories: List[BulkCategoryPreview]
    quizzes: List[BulkQuizPreview]
    questions: List[BulkQuestionPreview]
    warnings: List[str] = Field(default_factory=list)


class BulkCategoryPayload(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=16)


class BulkQuizPayload(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = Field(default=None)
    is_active: bool = True
    question_prompts: List[str] = Field(default_factory=list)


class BulkQuestionPayload(BaseModel):
    prompt: str = Field(..., min_length=1)
    explanation: str | None = Field(default=None)
    subject: str | None = Field(default=None)
    difficulty: str | None = Field(default=None)
    is_active: bool = True
    category_name: str = Field(..., min_length=1)
    quiz_titles: List[str] = Field(default_factory=list)
    options: List[BulkQuestionOption]


class BulkImportCommit(BaseModel):
    categories: List[BulkCategoryPayload] = Field(default_factory=list)
    quizzes: List[BulkQuizPayload] = Field(default_factory=list)
    questions: List[BulkQuestionPayload] = Field(default_factory=list)


class BulkImportResult(BaseModel):
    categories_created: int
    categories_updated: int
    quizzes_created: int
    quizzes_updated: int
    questions_created: int
    questions_updated: int

