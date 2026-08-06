"""Rule-based catalog search used by the demo API.

The catalog deliberately uses public, synthetic data.  It demonstrates why
structured metadata filters complement semantic PDF retrieval.
"""

import json
from functools import lru_cache
from pathlib import Path

from app.models import CatalogDocument, CatalogSearch

DATA_PATH = Path(__file__).resolve().parents[2] / "sample_data" / "catalog.json"


@lru_cache
def load_catalog() -> tuple[CatalogDocument, ...]:
    """Load and validate the static demo catalog once per process."""
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return tuple(CatalogDocument.model_validate(item) for item in raw)


def _matches_tag(values: list[str], requested: str | None) -> bool:
    """Match a tag while respecting the public catalog's `All` wildcard."""
    if not requested:
        return True
    normalized = requested.strip().casefold()
    return any(value.casefold() in {normalized, "all"} for value in values)


def search_catalog(filters: CatalogSearch) -> list[CatalogDocument]:
    matches = []
    for document in load_catalog():
        if not _matches_tag(document.lifecycle_stages, filters.lifecycle_stage):
            continue
        if not _matches_tag(document.topics, filters.topic):
            continue
        if filters.effective_from and document.effective_date < filters.effective_from:
            continue
        matches.append(document)
    return sorted(matches, key=lambda item: (item.effective_date, item.id), reverse=True)
