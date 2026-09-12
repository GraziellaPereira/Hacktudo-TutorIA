from pydantic import BaseModel


class TeacherReview(BaseModel):
    activity_id: str
    status: str
    teacher_comment: str | None = None