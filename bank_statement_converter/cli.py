from __future__ import annotations

import argparse
import logging



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert bank statement PDF to clean Excel format")
    parser.add_argument("input_pdf", help="Path to bank statement PDF")
    parser.add_argument("output_xlsx", help="Path to output .xlsx file")
    parser.add_argument(
        "--failed-rows",
        default="failed_rows.csv",
        help="CSV path to store rows that could not be parsed (default: failed_rows.csv)",
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    from .pipeline import convert_bank_statement

    convert_bank_statement(args.input_pdf, args.output_xlsx, args.failed_rows)


if __name__ == "__main__":
    main()
