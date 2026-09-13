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


class TopicUpdateRequest(BaseModel):
    id: str
    name: str
    description: str = ""
    learning_objectives: list[str] = []
    concepts: list[str] = []
    practical_applications: list[str] = []

class StudentCreateRequest(BaseModel):

    name: str

    education_level: str

    grade_or_period: str


class TeacherCreateRequest(BaseModel):
    name: str
    description: str
    email: str | None = None


class TeacherUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    email: str | None = None


class ContextCreateRequest(BaseModel):
    name: str
    description: str = ""


class ContextStructureUpdateRequest(BaseModel):
    classrooms: list = []
    subjects: list = []


class ContentUpdateRequest(BaseModel):
    title: str | None = None
    summary: str | None = None
    topics: list[TopicUpdateRequest] | None = None