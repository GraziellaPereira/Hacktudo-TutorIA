from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class StudentAttempt(BaseModel):
    student_id: str
    activity_id: str
    topic: str
    method: str | None = None
    selected_answer: str
    correct_answer: str
    is_correct: bool
    difficulty: int = Field(ge=1, le=5)
    learning_dimension: Literal["concept", "relationship", "specific_information", "application", "interpretation"]
    response_time_seconds: float | None = None
    created_at: datetime