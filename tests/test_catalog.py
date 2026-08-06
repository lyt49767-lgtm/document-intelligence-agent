from datetime import date

from app.models import CatalogSearch
from app.services.catalog import search_catalog


def test_all_lifecycle_stage_is_included():
    results = search_catalog(CatalogSearch(lifecycle_stage="Build"))
    assert {item.id for item in results} == {"DOC-001", "DOC-002"}


def test_all_topic_is_included():
    results = search_catalog(CatalogSearch(lifecycle_stage="Operate", topic="Security"))
    assert [item.id for item in results] == ["DOC-003"]


def test_effective_date_filter():
    results = search_catalog(CatalogSearch(effective_from=date(2026, 1, 1)))
    assert [item.id for item in results] == ["DOC-004"]
