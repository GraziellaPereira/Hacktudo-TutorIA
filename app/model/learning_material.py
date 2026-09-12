from typing import Literal

from pydantic import BaseModel, Field, model_validator


class LearningSummary(BaseModel):
    title: str
    summary: str


class Flashcard(BaseModel):
    id: str
    question: str
    hint: str
    answer: str
    difficulty: int = Field(ge=1, le=5)
    concept: str


class MindMapNode(BaseModel):
    id: str
    title: str
    keywords: list[str] = Field(min_length=2, max_length=6)
    summary: str = Field(min_length=20, max_length=300)
    concepts: list[str] = Field(min_length=1, max_length=6)
    children: list["MindMapNode | str"] = Field(default_factory=list)


class InfographicSection(BaseModel):
    id: str
    title: str
    content: str = Field(min_length=20, max_length=240)
    key_points: list[str] = Field(min_length=2, max_length=5)


class LearningMaterial(BaseModel):
    method: Literal["flashcards", "mind_map", "infographic"]
    title: str
    summary: str

    flashcards: list[Flashcard] = Field(default_factory=list)
    mind_map: list[MindMapNode] = Field(default_factory=list)
    infographic_sections: list[InfographicSection] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_method_content(self):
        if self.method == "flashcards" and len(self.flashcards) < 8:
            raise ValueError(
                "O método flashcards deve possuir pelo menos 8 flashcards."
            )

        if self.method == "mind_map" and not self.mind_map:
            raise ValueError(
                "O método mind_map deve possuir pelo menos um nó."
            )

        if self.method == "mind_map":
            node_count = 0

            def count_nodes(nodes):
                total = 0
                for node in nodes:
                    total += 1
                    if isinstance(node, MindMapNode):
                        total += count_nodes(node.children)
                return total

            node_count = count_nodes(self.mind_map)
            if node_count < 3:
                raise ValueError(
                    "O mapa mental deve possuir pelo menos três nós relacionados."
                )

            if not any(node.children for node in self.mind_map):
                raise ValueError(
                    "O mapa mental deve possuir pelo menos uma relação entre nós."
                )

        if self.method == "infographic" and len(self.infographic_sections) < 3:
            raise ValueError(
                "O método infographic deve possuir pelo menos três seções."
            )

        return self