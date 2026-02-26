import unittest

import pandas as pd

from bank_statement_converter.parser import parse_rows_to_transactions
from bank_statement_converter.utils import parse_amount


class ParserUtilsTests(unittest.TestCase):
    def test_parse_amount_handles_plain_numbers_and_commas(self) -> None:
        self.assertEqual(parse_amount("1234.56"), 1234.56)
        self.assertEqual(parse_amount("1,234.56"), 1234.56)
        self.assertEqual(parse_amount("(2,000.00)"), -2000.0)

    def test_parser_distinguishes_dr_cr_and_multiline_narration(self) -> None:
        raw_rows = [
            ["Date", "Narration", "Debit", "Credit", "Balance"],
            ["01/01/2024", "ATM CASH", "1,000.00 Dr", "", "10,000.00"],
            ["continued line for narration"],
            ["02/01/2024", "NEFT CREDIT", "", "2,500.00 Cr", "12,500.00"],
        ]

        tx_df, rejected_df = parse_rows_to_transactions(raw_rows)

        self.assertEqual(len(tx_df), 2)
        self.assertEqual(len(rejected_df), 0)

        first = tx_df.iloc[0].to_dict()
        second = tx_df.iloc[1].to_dict()

        self.assertEqual(first["debit"], 1000.0)
        self.assertTrue(pd.isna(first["credit"]))
        self.assertIn("continued line for narration", first["narration"])

        self.assertEqual(second["credit"], 2500.0)
        self.assertTrue(pd.isna(second["debit"]))


if __name__ == "__main__":
    unittest.main()
