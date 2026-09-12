from pydantic import BaseModel, Field


class Topic(BaseModel):
    name: str
    description: str
    importance: int
    difficulty: int
    learning_objectives: list[str]
    concepts: list[str]
    practical_applications: list[str]


class ContentAnalysis(BaseModel):
    title: str
    summary: str
    topics: list[Topic] = Field(min_length=3)