"""Minimal, inspectable extraction for text-based PDFs."""

from typing import Any

import fitz


def _bbox(rect: Any) -> list[float]:
    return [round(float(value), 2) for value in rect]


def extract_pdf(content: bytes, max_pages: int = 10) -> dict[str, Any]:
    """Extract page text blocks and native tables without persisting uploads."""
    document = fitz.open(stream=content, filetype="pdf")
    page_count = min(len(document), max_pages)
    pages: list[dict[str, Any]] = []

    for index in range(page_count):
        page = document[index]
        items: list[dict[str, Any]] = []
        table_regions: list[fitz.Rect] = []

        try:
            tables = page.find_tables()
            for table in tables.tables:
                rect = fitz.Rect(table.bbox)
                table_regions.append(rect)
                rows = table.extract()
                items.append(
                    {
                        "type": "table",
                        "bbox": _bbox(rect),
                        "rows": [[cell or "" for cell in row] for row in rows],
                    }
                )
        except Exception:
            # Some PDFs have no table structure or unsupported vector content.
            pass

        for block in page.get_text("blocks"):
            x0, y0, x1, y1, text, block_no, block_type = block[:7]
            if block_type != 0 or not text.strip():
                continue
            rect = fitz.Rect(x0, y0, x1, y1)
            if any((rect & table_rect).get_area() > rect.get_area() * 0.5 for table_rect in table_regions):
                continue
            items.append({"type": "text", "bbox": _bbox(rect), "content": text.strip()})

        items.sort(key=lambda item: (item["bbox"][1], item["bbox"][0]))
        pages.append(
            {
                "page": index + 1,
                "width": round(page.rect.width, 2),
                "height": round(page.rect.height, 2),
                "items": items,
            }
        )

    return {
        "pages_processed": page_count,
        "total_pages": len(document),
        "truncated": len(document) > page_count,
        "pages": pages,
    }
