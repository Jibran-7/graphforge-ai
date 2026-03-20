from pydantic import BaseModel, ConfigDict, Field, field_validator


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    name: str = Field(min_length=1)
    entity_type: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("entity name must not be empty")
        return cleaned


class RelationshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    source_entity_id: int
    target_entity_id: int
    relation_type: str = Field(min_length=1)
    evidence_text: str | None

    @field_validator("relation_type")
    @classmethod
    def validate_relation_type(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("relation_type must not be empty")
        return cleaned.upper()


class GraphResponse(BaseModel):
    document_id: int
    entities: list[EntityResponse]
    relationships: list[RelationshipResponse]


class GraphSummaryResponse(BaseModel):
    document_id: int
    entity_count: int
    relationship_count: int
    top_entity_names: list[str]
