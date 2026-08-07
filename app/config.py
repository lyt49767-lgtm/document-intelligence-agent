"""Application settings loaded from environment variables."""

from functools import lru_cache
from os import getenv

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_upload_limit() -> int:
    """Respect Vercel's function request limit while keeping Docker more permissive."""
    if getenv("VERCEL"):
        return 4 * 1024 * 1024
    return 12 * 1024 * 1024


class Settings(BaseSettings):
    """Runtime settings with safe defaults for the public project."""

    model_config = SettingsConfigDict(env_prefix="DOCUMENT_AGENT_", case_sensitive=False)

    max_upload_bytes: int = Field(default_factory=_default_upload_limit, ge=1, le=50 * 1024 * 1024)
    max_pages: int = Field(default=10, ge=1, le=100)
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")


@lru_cache
def get_settings() -> Settings:
    """Return one immutable settings object per process."""
    return Settings()
