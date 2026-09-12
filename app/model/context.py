from pydantic import BaseModel


class LearningContext(BaseModel):
    subject: str
    education_level: str
    grade_or_period: str
    target_audience: str
    learning_goal: str
    assessment_focus: list[str] | None = None