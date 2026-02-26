from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class TransactionRow:
    date: str
    narration: str
    particulars: str
    debit: float | None
    credit: float | None
    balance: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
