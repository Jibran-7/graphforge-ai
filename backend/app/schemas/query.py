from pydantic import BaseModel, Field, field_validator


class GraphQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    document_id: int | None = None

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("question must not be empty")
        return cleaned


class PathStep(BaseModel):
    source_entity: str
    relation_type: str = Field(min_length=1)
    target_entity: str
    evidence_text: str | None

    @field_validator("relation_type")
    @classmethod
    def validate_relation_type(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("relation_type must not be empty")
        return cleaned


class GraphQueryResponse(BaseModel):
    question: str
    answer: str
    matched_entities: list[str]
    paths: list[PathStep]
