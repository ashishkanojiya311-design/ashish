from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_to_excel(df: pd.DataFrame, output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    export_df = df.copy()
    export_df = export_df.rename(
        columns={
            "date": "Date",
            "narration": "Narration / Description",
            "particulars": "Particulars",
            "debit": "Debit (Dr – withdrawal)",
            "credit": "Credit (Cr – deposit)",
            "balance": "Balance",
        }
    )

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Transactions")
