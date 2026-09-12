from pydantic import BaseModel


class ActivityValidation(BaseModel):
    approved: bool
    score: int
    errors: list[str]
    warnings: list[str]