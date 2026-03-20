from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="GraphForge Intelligence Platform API", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    app_host: str = Field(default="127.0.0.1", validation_alias="APP_HOST")
    app_port: int = Field(default=8000, validation_alias="APP_PORT")
    database_url: str = Field(default="sqlite:///./graphforge.db", validation_alias="DATABASE_URL")
    upload_dir: str = Field(default="uploads", validation_alias="UPLOAD_DIR")
    max_upload_size_mb: int = Field(default=25, validation_alias="MAX_UPLOAD_SIZE_MB")
    allowed_file_types: list[str] = Field(
        default_factory=lambda: ["pdf", "docx", "txt", "md"],
        validation_alias="ALLOWED_FILE_TYPES",
    )

    @field_validator("allowed_file_types", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip().lower() for item in value.split(",") if item.strip()]
        return [item.strip().lower() for item in value]


@lru_cache
def get_settings() -> Settings:
    return Settings()
