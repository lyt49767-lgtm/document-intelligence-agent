from datetime import date
from typing import Any, Literal

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


class ToolCall(BaseModel):
    """An auditable record of one tool selected by the agent."""

    tool: Literal["catalog_search", "pdf_extract"]
    reason: str
    input: dict[str, Any]


class Citation(BaseModel):
    """A source returned alongside the agent response."""

    source_type: Literal["catalog", "pdf"]
    title: str
    document_id: str | None = None
    page: int | None = None
    excerpt: str | None = None


class AgentResponse(BaseModel):
    """Traceable output from the deterministic document agent."""

    route: Literal["catalog_search", "pdf_extraction", "hybrid", "guidance"]
    answer: str
    tool_calls: list[ToolCall]
    citations: list[Citation]
    results: list[CatalogDocument] = Field(default_factory=list)
