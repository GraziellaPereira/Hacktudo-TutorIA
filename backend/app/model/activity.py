from pydantic import BaseModel, Field, model_validator
from typing import Literal
from uuid import uuid4


class Activity(BaseModel):
    activity_id: str = Field(
    default_factory=lambda: str(uuid4())
)
    learning_dimension: Literal [
    "concept",
    "relationship",
    "specific_information",
    "application",
    "interpretation",        
    ]

    topic: str

    learning_objective: str

    type: str

    difficulty: int = Field(
        ge=1,
        le=5
    )

    cognitive_skill: str

    question: str

    options: list[str] = Field(
        min_length=4,
        max_length=4
    )

    correct_answer: str

    explanation: str

    hints: list[str] = Field(
        min_length=3,
        max_length=3
    )


    # Controle da revisão do professor
    review_status: Literal[
    "pending",
    "approved",
    "edited",
    "regenerated",
    "rejected"
] = "pending"

    validation_score: int | None = None

    validation_warnings: list[str] = []

    teacher_modified: bool = False


    @model_validator(mode="after")
    def validate_answer(self):

        if len(set(self.options)) != 4:
            raise ValueError(
                "As alternativas devem ser diferentes"
            )

        if self.correct_answer not in self.options:
            raise ValueError(
                "A resposta correta deve ser exatamente uma das alternativas"
            )

        return self



class ActivitySet(BaseModel):

    activities: list[Activity] = Field(
        min_length=5
    )


    @model_validator(mode="after")
    def validate_difficulty_distribution(self):

        difficulties = {
            activity.difficulty
            for activity in self.activities
        }


        if not difficulties.intersection({1, 2}):
            raise ValueError(
                "É necessária pelo menos uma questão fácil"
            )


        if 3 not in difficulties:
            raise ValueError(
                "É necessária pelo menos uma questão média"
            )


        if not difficulties.intersection({4, 5}):
            raise ValueError(
                "É necessária pelo menos uma questão difícil"
            )


        return self