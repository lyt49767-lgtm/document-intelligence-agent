from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class CatalogSearch(BaseModel):
    """Safe, structured filters for the public demo catalog."""

    lifecycle_stage: str | None = Field(default=None, max_length=64)
    topic: str | None = Field(default=None, max_length=64)
    effective_from: date | None = None


class CatalogDocument(BaseModel):
    id: str
    title: str
    lifecycle_stages: list[str]
    topics: list[str]
    effective_date: date
    document_type: Literal["policy", "guide", "template", "reference"]
    summary: str
