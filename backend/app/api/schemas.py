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

class StudentCreateRequest(BaseModel):

    name: str

    education_level: str

    grade_or_period: str


class TeacherCreateRequest(BaseModel):
    name: str
    description: str
    email: str | None = None


class ContextCreateRequest(BaseModel):
    name: str
    description: str = ""


class ContextStructureUpdateRequest(BaseModel):
    classrooms: list = []
    subjects: list = []