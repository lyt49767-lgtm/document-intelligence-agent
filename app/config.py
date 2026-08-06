"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings with safe defaults for the public demo."""

    model_config = SettingsConfigDict(env_prefix="DOCUMENT_AGENT_", case_sensitive=False)

    max_upload_bytes: int = Field(default=12 * 1024 * 1024, ge=1, le=50 * 1024 * 1024)
    max_pages: int = Field(default=10, ge=1, le=100)
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")


@lru_cache
def get_settings() -> Settings:
    """Return one immutable settings object per process."""
    return Settings()
