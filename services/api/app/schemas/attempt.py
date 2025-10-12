from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AttemptAnswerIn(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None


class AttemptCreate(BaseModel):
    quiz_id: int
    answers: List[AttemptAnswerIn]
    started_at: Optional[datetime] = None
    duration_seconds: Optional[int] = Field(default=None, ge=0)


class AttemptAnswerOption(BaseModel):
    id: int
    text: str


class AttemptAnswerReview(BaseModel):
    question_id: int
    prompt: str
    explanation: Optional[str]
    selected_option_id: Optional[int]
    correct_option_id: Optional[int]
    is_correct: bool
    options: List[AttemptAnswerOption]


class AttemptResult(BaseModel):
    id: int
    quiz_id: int
    quiz_title: str
    submitted_at: datetime
    total_questions: int
    correct_answers: int
    score: float
    answers: List[AttemptAnswerReview]

    model_config = {
        "from_attributes": True,
    }


class AttemptHistoryEntry(BaseModel):
    id: int
    quiz_id: int
    quiz_title: str
    submitted_at: datetime
    total_questions: int
    correct_answers: int
    score: float
    duration_seconds: int
    subject_id: Optional[int] = None
    subject_name: Optional[str] = None
    difficulty: str
    type: str = "quiz"

    model_config = {
        "from_attributes": True,
    }
