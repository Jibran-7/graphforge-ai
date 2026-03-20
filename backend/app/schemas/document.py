from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentCreate(BaseModel):
    filename: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    file_size: int = Field(gt=0)

    @field_validator("filename", "content_type")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty")
        return cleaned


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    file_path: str
    file_size: int
    uploaded_at: datetime


class DocumentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    file_path: str
    file_size: int
    uploaded_at: datetime
    extracted_text: str | None
