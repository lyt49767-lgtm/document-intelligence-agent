import fitz
from fastapi.testclient import TestClient

from api.index import app as vercel_app
from app.main import app


def _pdf_with_text(text: str = "Hello document agent") -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def test_health_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_vercel_entrypoint_exports_the_application() -> None:
    assert vercel_app is app


def test_parse_extracts_text_from_pdf() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/parse",
        files={"file": ("demo.pdf", _pdf_with_text(), "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_pages"] == 1
    assert body["pages_processed"] == 1
    assert body["pages"][0]["items"][0]["content"] == "Hello document agent"


def test_parse_rejects_non_pdf_upload() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/parse",
        files={"file": ("notes.txt", b"not a PDF", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Please upload a PDF file."


def test_parse_returns_422_for_invalid_pdf() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/parse",
        files={"file": ("invalid.pdf", b"not a valid PDF", "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Unable to parse this PDF."


def test_agent_routes_catalog_question_to_search() -> None:
    client = TestClient(app)

    response = client.post("/api/ask", data={"question": "Find Build security documents"})

    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "catalog_search"
    assert body["tool_calls"][0]["tool"] == "catalog_search"
    assert body["results"]


def test_agent_returns_pdf_page_citations() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/ask",
        data={"question": "Summarize this uploaded document"},
        files={"file": ("evidence.pdf", _pdf_with_text("Page evidence"), "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "hybrid"
    assert any(citation["page"] == 1 for citation in body["citations"])
