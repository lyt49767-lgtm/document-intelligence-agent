"""Deterministic tool routing for the Document Intelligence Agent."""

from typing import Any, Literal

from app.models import AgentResponse, CatalogSearch, Citation, ToolCall
from app.services.catalog import search_catalog

STAGE_KEYWORDS = {
    "plan": "Plan",
    "planning": "Plan",
    "规划": "Plan",
    "build": "Build",
    "开发": "Build",
    "构建": "Build",
    "operate": "Operate",
    "operation": "Operate",
    "运维": "Operate",
}
TOPIC_KEYWORDS = {
    "security": "Security",
    "安全": "Security",
    "quality": "Quality",
    "质量": "Quality",
    "delivery": "Delivery",
    "交付": "Delivery",
}
CATALOG_KEYWORDS = {"find", "search", "catalog", "document", "查找", "检索", "文档"}


def _first_matching_value(question: str, mapping: dict[str, str]) -> str | None:
    return next((value for keyword, value in mapping.items() if keyword in question), None)


def _pdf_citations(pdf_result: dict[str, Any], filename: str) -> list[Citation]:
    citations: list[Citation] = []
    for page in pdf_result["pages"]:
        for item in page["items"]:
            if item["type"] != "text":
                continue
            excerpt = item["content"].replace("\n", " ")[:240]
            citations.append(
                Citation(source_type="pdf", title=filename, page=page["page"], excerpt=excerpt)
            )
            if len(citations) == 3:
                return citations
    return citations


def run_agent(
    question: str, pdf_result: dict[str, Any] | None = None, filename: str = ""
) -> AgentResponse:
    """Select and run available tools without requiring an external model API."""
    normalized = question.casefold()
    lifecycle_stage = _first_matching_value(normalized, STAGE_KEYWORDS)
    topic = _first_matching_value(normalized, TOPIC_KEYWORDS)
    use_catalog = bool(
        lifecycle_stage or topic or any(word in normalized for word in CATALOG_KEYWORDS)
    )
    tool_calls: list[ToolCall] = []
    citations: list[Citation] = []
    results = []

    if use_catalog:
        filters = CatalogSearch(lifecycle_stage=lifecycle_stage, topic=topic)
        results = search_catalog(filters)
        tool_calls.append(
            ToolCall(
                tool="catalog_search",
                reason="The question includes a document-discovery intent or structured metadata.",
                input=filters.model_dump(mode="json"),
            )
        )
        citations.extend(
            Citation(
                source_type="catalog",
                title=item.title,
                document_id=item.id,
                excerpt=item.summary,
            )
            for item in results
        )

    if pdf_result is not None:
        tool_calls.append(
            ToolCall(
                tool="pdf_extract",
                reason="A PDF was supplied, so the agent extracted its page-level structure.",
                input={"filename": filename, "pages_processed": pdf_result["pages_processed"]},
            )
        )
        citations.extend(_pdf_citations(pdf_result, filename))

    route: Literal["catalog_search", "pdf_extraction", "hybrid", "guidance"]
    if use_catalog and pdf_result is not None:
        route = "hybrid"
    elif use_catalog:
        route = "catalog_search"
    elif pdf_result is not None:
        route = "pdf_extraction"
    else:
        route = "guidance"

    if route == "hybrid":
        assert pdf_result is not None
        answer = (
            f"Searched the catalog and extracted {pdf_result['pages_processed']} PDF page(s). "
            f"Found {len(results)} matching catalog document(s); see the cited sources below."
        )
    elif route == "catalog_search":
        answer = f"Found {len(results)} catalog document(s) matching the detected conditions."
    elif route == "pdf_extraction":
        assert pdf_result is not None
        answer = (
            f"Extracted {pdf_result['pages_processed']} of "
            f"{pdf_result['total_pages']} PDF page(s). "
            "The returned citations contain page-level evidence."
        )
    else:
        answer = (
            "Ask to find a document by stage or topic, or attach a PDF for structure extraction."
        )

    return AgentResponse(
        route=route,
        answer=answer,
        tool_calls=tool_calls,
        citations=citations,
        results=results,
    )
