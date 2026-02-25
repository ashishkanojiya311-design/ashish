from __future__ import annotations

import logging
import re
from collections.abc import Iterable

import pandas as pd

from .models import TransactionRow
from .utils import coalesce_text, normalize_whitespace, parse_amount, parse_date

logger = logging.getLogger(__name__)

HEADER_TOKENS = {
    "date",
    "narration",
    "description",
    "particulars",
    "withdrawal",
    "deposit",
    "debit",
    "credit",
    "balance",
}

DR_CR_TOKEN = re.compile(r"\b(dr|cr)\b", re.IGNORECASE)


def _is_header_row(cells: Iterable[str]) -> bool:
    joined = " ".join(normalize_whitespace(c).lower() for c in cells if c)
    score = sum(token in joined for token in HEADER_TOKENS)
    return score >= 2


def _split_row(row: list[str]) -> tuple[str | None, str, list[str]]:
    """Returns parsed date, narration fragment, and numeric/raw tail cells."""
    cleaned = [normalize_whitespace(str(cell)) for cell in row if normalize_whitespace(str(cell))]
    if not cleaned:
        return None, "", []

    date_value = parse_date(cleaned[0])
    if date_value:
        if len(cleaned) == 1:
            return date_value, "", []
        return date_value, cleaned[1], cleaned[2:]

    return None, cleaned[0], cleaned[1:]


def _extract_amounts_from_tail(tail: list[str]) -> tuple[float | None, float | None, float | None]:
    debit = credit = balance = None

    # Strong signal: explicit Dr/Cr markers.
    for i, cell in enumerate(tail):
        marker = DR_CR_TOKEN.search(cell)
        amount = parse_amount(cell)
        if marker and amount is not None:
            if marker.group(1).lower() == "dr":
                debit = amount
            else:
                credit = amount

        # check adjacent split marker e.g. ["1,000.00", "Dr"]
        if amount is not None and i + 1 < len(tail):
            marker_next = DR_CR_TOKEN.search(tail[i + 1])
            if marker_next:
                if marker_next.group(1).lower() == "dr":
                    debit = amount
                else:
                    credit = amount

    numbers = [parse_amount(x) for x in tail]
    numbers = [n for n in numbers if n is not None]

    if debit is None and credit is None:
        if len(numbers) == 1:
            # Unknown direction with single amount: treat as credit by default only if markers suggest deposit.
            credit = numbers[0]
        elif len(numbers) >= 2:
            debit, credit = numbers[0], numbers[1]

    if len(numbers) >= 3:
        balance = numbers[-1]
    elif len(numbers) == 2 and (debit is not None or credit is not None):
        if debit is not None and credit is None:
            balance = numbers[-1] if numbers[-1] != debit else None
        elif credit is not None and debit is None:
            balance = numbers[-1] if numbers[-1] != credit else None

    if debit is not None and credit is not None:
        # If both populated but one is zero, clean up.
        if abs(debit) < 1e-9:
            debit = None
        if abs(credit) < 1e-9:
            credit = None

    return debit, credit, balance


def parse_rows_to_transactions(raw_rows: list[list[str]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    transactions: list[TransactionRow] = []
    rejected: list[dict[str, str]] = []

    last_txn: TransactionRow | None = None

    for raw_row in raw_rows:
        if not raw_row:
            continue

        text_cells = [normalize_whitespace(str(c)) for c in raw_row]
        if _is_header_row(text_cells):
            continue

        date_value, narration_fragment, tail = _split_row(text_cells)

        if date_value:
            debit, credit, balance = _extract_amounts_from_tail(tail)
            particulars = coalesce_text(t for t in tail if parse_amount(t) is None)

            txn = TransactionRow(
                date=date_value,
                narration=narration_fragment,
                particulars=particulars,
                debit=debit,
                credit=credit,
                balance=balance,
            )
            transactions.append(txn)
            last_txn = txn
            continue

        # Multi-line continuation row if it lacks date but includes text.
        continuation_text = coalesce_text([narration_fragment] + tail)
        if continuation_text and last_txn:
            last_txn.narration = coalesce_text([last_txn.narration, continuation_text])
            continue

        if continuation_text:
            rejected.append({"raw_row": " | ".join(text_cells), "reason": "Could not detect transaction date"})

    tx_df = pd.DataFrame([t.to_dict() for t in transactions], columns=["date", "narration", "particulars", "debit", "credit", "balance"])
    rejected_df = pd.DataFrame(rejected, columns=["raw_row", "reason"])

    logger.info("Parsed %s rows into %s transactions (%s rejected)", len(raw_rows), len(tx_df), len(rejected_df))
    return tx_df, rejected_df
