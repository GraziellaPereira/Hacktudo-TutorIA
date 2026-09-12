from pydantic import BaseModel


class StudentContext(BaseModel):

    student_id: str

    education_level: str

    grade_or_period: str

    preferred_method: str | None = None

    learning_difficulty: str | None = None