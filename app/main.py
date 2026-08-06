import logging
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models import CatalogSearch
from app.services.catalog import load_catalog, search_catalog
from app.services.pdf_extract import extract_pdf

APP_DIR = Path(__file__).resolve().parent
settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Agent Demo",
    version="1.0.0",
    description="A privacy-safe demo for PDF structure extraction and catalog retrieval.",
)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(APP_DIR / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/catalog")
def catalog() -> list[dict]:
    return [item.model_dump(mode="json") for item in load_catalog()]


@app.post("/api/search")
def search(filters: CatalogSearch) -> dict:
    results = search_catalog(filters)
    return {"count": len(results), "results": [item.model_dump(mode="json") for item in results]}


@app.post("/api/parse")
async def parse_pdf(file: Annotated[UploadFile, File(...)]) -> dict:
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=415, detail="Please upload a PDF file.")
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"PDF exceeds the {settings.max_upload_bytes // 1024 // 1024} MB demo limit.",
        )
    try:
        result = extract_pdf(content, max_pages=settings.max_pages)
        logger.info(
            "pdf_parsed filename=%s total_pages=%s processed_pages=%s",
            file.filename,
            result["total_pages"],
            result["pages_processed"],
        )
        return result
    except Exception as exc:
        logger.warning("pdf_parse_failed filename=%s", file.filename, exc_info=exc)
        raise HTTPException(status_code=422, detail="Unable to parse this PDF.") from exc
