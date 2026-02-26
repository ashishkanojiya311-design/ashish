from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .extractors import extract_raw_rows
from .parser import parse_rows_to_transactions
from .utils import remove_duplicates_and_blanks
from .writer import write_to_excel

logger = logging.getLogger(__name__)


def convert_bank_statement(
    input_pdf: str | Path,
    output_xlsx: str | Path,
    failed_rows_path: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    input_path = Path(input_pdf)
    if not input_path.exists():
        raise FileNotFoundError(f"PDF not found: {input_path}")

    raw_rows, mode = extract_raw_rows(input_path)
    logger.info("Extraction mode: %s, raw rows: %s", mode, len(raw_rows))

    tx_df, rejected_df = parse_rows_to_transactions(raw_rows)
    cleaned = remove_duplicates_and_blanks(tx_df)

    write_to_excel(cleaned, output_xlsx)
    logger.info("Wrote %s clean transactions to %s", len(cleaned), output_xlsx)

    if failed_rows_path:
        failed_path = Path(failed_rows_path)
        failed_path.parent.mkdir(parents=True, exist_ok=True)
        rejected_df.to_csv(failed_path, index=False)
        logger.info("Wrote %s rejected rows to %s", len(rejected_df), failed_rows_path)

    return cleaned, rejected_df
