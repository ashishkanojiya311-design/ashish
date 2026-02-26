#!/usr/bin/env python3
"""Simple conversion script for bank statement PDFs to Excel.

Usage:
  python conversion_script.py input.pdf output.xlsx --failed-rows failed_rows.csv
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from bank_statement_converter import convert_bank_statement


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert bank statement PDF into Excel")
    parser.add_argument("input_pdf", type=Path, help="Path to source bank statement PDF")
    parser.add_argument("output_xlsx", type=Path, help="Path to destination .xlsx file")
    parser.add_argument(
        "--failed-rows",
        type=Path,
        default=None,
        help="Optional CSV file path where unparsed rows will be logged",
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level: DEBUG, INFO, WARNING, ERROR")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    try:
        cleaned_df, rejected_df = convert_bank_statement(
            input_pdf=args.input_pdf,
            output_xlsx=args.output_xlsx,
            failed_rows_path=args.failed_rows,
        )
    except Exception as exc:
        logging.error("Conversion failed: %s", exc)
        return 1

    logging.info("Conversion complete: %s rows exported, %s rows rejected", len(cleaned_df), len(rejected_df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
