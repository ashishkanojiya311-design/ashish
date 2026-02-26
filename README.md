# Bank Statement PDF to Excel Converter

A modular Python application that extracts transaction tables from bank statement PDFs and exports clean `.xlsx` output.

## Features

- Extracts structured transaction data from **text-based PDFs** using `pdfplumber` (with `camelot` fallback).
- Supports **scanned PDFs** using OCR (`pytesseract` + `pdf2image`).
- Produces normalized columns:
  - Date
  - Narration / Description
  - Particulars
  - Debit (Dr – withdrawal)
  - Credit (Cr – deposit)
  - Balance (if available)
- Handles multi-line narrations by appending continuation rows.
- Cleans dates/amounts, removes duplicates and blank rows.
- Logs rows that cannot be parsed to CSV.

## Project Structure

- `bank_statement_converter/extractors.py` – PDF table extraction (text + OCR modes).
- `bank_statement_converter/parser.py` – transaction parsing and debit/credit detection.
- `bank_statement_converter/utils.py` – normalization helpers.
- `bank_statement_converter/writer.py` – Excel export.
- `bank_statement_converter/pipeline.py` – end-to-end orchestration.
- `bank_statement_converter/cli.py` – command line interface.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

> OCR mode additionally requires system dependencies:
> - Tesseract OCR binary installed and available on PATH
> - Poppler (required by `pdf2image`)

## Usage

```bash
bank-statement-converter <input.pdf> <output.xlsx> --failed-rows failed_rows.csv
```

Example:

```bash
bank-statement-converter ./samples/statement.pdf ./output/statement.xlsx --failed-rows ./output/unparsed_rows.csv
```


Alternative standalone script (without installing console entrypoint):

```bash
python conversion_script.py <input.pdf> <output.xlsx> --failed-rows failed_rows.csv
```

## Notes on Accuracy

- Explicit `Dr`/`Cr` markers are prioritized when assigning debit vs credit.
- Where markers are absent, numeric columns are interpreted by position (common statement layout assumptions).
- You may tune parsing logic in `parser.py` for bank-specific formats.

## Programmatic Use

```python
from bank_statement_converter import convert_bank_statement

cleaned_df, rejected_df = convert_bank_statement(
    input_pdf="statement.pdf",
    output_xlsx="statement.xlsx",
    failed_rows_path="failed_rows.csv",
)
```
