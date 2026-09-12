from typing import Optional
from pydantic import BaseModel


class ActivityReviewRequest(BaseModel):

    review_status: str

    teacher_modified: bool = False

    question: Optional[str] = None

    options: Optional[list[str]] = None

    correct_answer: Optional[str] = None

    explanation: Optional[str] = None

    hints: Optional[list[str]] = None