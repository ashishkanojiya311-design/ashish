"""Bank statement PDF to Excel converter package."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd



def convert_bank_statement(
    input_pdf: str | Path,
    output_xlsx: str | Path,
    failed_rows_path: str | Path | None = None,
) -> tuple["pd.DataFrame", "pd.DataFrame"]:
    """Lazy package-level entrypoint to avoid importing heavy deps on package import."""
    from .pipeline import convert_bank_statement as _convert_bank_statement

    return _convert_bank_statement(input_pdf, output_xlsx, failed_rows_path)


__all__ = ["convert_bank_statement"]
