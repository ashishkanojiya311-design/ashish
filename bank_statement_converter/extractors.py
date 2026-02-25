from __future__ import annotations

import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_tables_from_text_pdf(pdf_path: str | Path) -> list[list[list[str]]]:
    """Extract table-like rows from text PDFs using pdfplumber, fallback to camelot."""
    path = str(pdf_path)
    all_rows: list[list[list[str]]] = []

    import pdfplumber

    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_tables = page.extract_tables(
                {
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 3,
                    "join_tolerance": 3,
                }
            ) or []
            if page_tables:
                all_rows.extend(page_tables)
                continue

            page_tables = page.extract_tables() or []
            if page_tables:
                all_rows.extend(page_tables)
                continue

            text_rows = [line.split("  ") for line in (page.extract_text() or "").splitlines() if line.strip()]
            if text_rows:
                all_rows.append(text_rows)
                logger.debug("Used line parsing on page %s", page_number)

    if all_rows:
        return all_rows

    # Fallback to camelot only when pdfplumber yields nothing.
    try:
        import camelot

        camelot_tables = camelot.read_pdf(path, pages="all", flavor="stream")
        for table in camelot_tables:
            all_rows.append(table.df.values.tolist())
    except Exception as exc:  # pragma: no cover - fallback/optional dependency
        logger.warning("Camelot fallback failed: %s", exc)

    return all_rows


def _pdf_has_extractable_text(pdf_path: str | Path, sample_pages: int = 2) -> bool:
    import pdfplumber

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages[:sample_pages]:
            if (page.extract_text() or "").strip():
                return True
    return False


def extract_rows_with_ocr(pdf_path: str | Path) -> list[list[str]]:
    """OCR based extraction for scanned PDFs."""
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except Exception as exc:  # pragma: no cover - optional dependency runtime
        raise RuntimeError("OCR dependencies missing: install pytesseract and pdf2image") from exc

    rows: list[list[str]] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        images = convert_from_path(str(pdf_path), dpi=300, output_folder=temp_dir)
        for image in images:
            text = pytesseract.image_to_string(image)
            for line in text.splitlines():
                if line.strip():
                    rows.append(line.split())
    return rows


def extract_raw_rows(pdf_path: str | Path) -> tuple[list[list[str]], str]:
    """Returns rows and extraction mode (text|ocr)."""
    if _pdf_has_extractable_text(pdf_path):
        tables = extract_tables_from_text_pdf(pdf_path)
        flat_rows = [row for table in tables for row in table]
        return flat_rows, "text"

    rows = extract_rows_with_ocr(pdf_path)
    return rows, "ocr"
