from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable

import pandas as pd

DATE_PATTERNS = (
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d/%m/%y",
    "%d-%m-%y",
    "%Y-%m-%d",
    "%d %b %Y",
    "%d %B %Y",
)

# Supports comma-grouped and plain digit amounts, with optional sign and decimal.
AMOUNT_REGEX = re.compile(r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_date(value: str) -> str | None:
    if not value:
        return None
    candidate = normalize_whitespace(value)
    for fmt in DATE_PATTERNS:
        try:
            return datetime.strptime(candidate, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Fuzzy cleanup e.g., 01.02.2024
    candidate = candidate.replace(".", "/")
    for fmt in DATE_PATTERNS:
        try:
            return datetime.strptime(candidate, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_amount(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = normalize_whitespace(str(value)).replace("₹", "").replace("INR", "")
    if not text:
        return None

    # Handle brackets as negative amounts
    if text.startswith("(") and text.endswith(")"):
        text = f"-{text[1:-1]}"

    compact = text.replace(" ", "")
    match = AMOUNT_REGEX.search(compact)
    if not match:
        return None

    try:
        amount = Decimal(match.group(0).replace(",", ""))
    except InvalidOperation:
        return None
    return float(amount)


def coalesce_text(parts: Iterable[str]) -> str:
    return normalize_whitespace(" ".join([p for p in parts if p]))


def remove_duplicates_and_blanks(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    filtered = filtered.dropna(how="all")

    key_cols = ["date", "narration", "particulars", "debit", "credit", "balance"]
    for column in key_cols:
        if column in filtered.columns:
            filtered[column] = filtered[column].replace("", pd.NA)
    filtered = filtered.dropna(subset=["date", "narration"], how="all")
    filtered = filtered.drop_duplicates(subset=key_cols, keep="first")
    return filtered.reset_index(drop=True)
