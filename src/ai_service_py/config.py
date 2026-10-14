"""Настройки приложения на базе Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="forbid",
        case_sensitive=False,
    )

    app_name: str = "ai-service-py"
    version: str = "1.0.0"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    http_timeout_seconds: float = Field(default=10.0, gt=0, le=300)

    llm_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen3-coder-next-agent:latest"
    llm_timeout_seconds: float = Field(default=300.0, gt=0)

    default_chunk_size: int = Field(default=500, gt=0)
    default_overlap: int = Field(default=50, ge=0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_production(self) -> bool:
        return not self.debug


@lru_cache
def get_settings() -> Settings:
    return Settings()
