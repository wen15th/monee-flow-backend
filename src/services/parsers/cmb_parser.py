from .base import BaseBankParser
from .utils import normalize_description, parse_date, first_non_empty

import decimal


class CMBBankParser(BaseBankParser):
    """
    CMB (China Merchant Bank) CSV parser.

    System-wide convention:
      - amount > 0  => expense
      - amount < 0  => income (ignored by BaseBankParser)
    """

    def get_csv_header(self):
        # CMB CSV already has header row
        # ["Date", "Currency", "Amount"/"Transaction Amount", "Balance", "Type", "Counterparty"]
        return None

    def extract_transaction_fields(self, item: dict):
        # Amount
        raw_amount = first_non_empty(item, "Amount", "Transaction Amount")
        if not raw_amount or raw_amount.lower() in {
            "nan",
            "none",
            "null",
            "n/a",
            "-",
            "--",
        }:
            return None, None, None

        cleaned = (
            raw_amount.replace(",", "")
            .replace("¥", "")
            .replace("￥", "")
            .replace("$", "")
            .strip()
        )

        # (123.45) -> -123.45
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = "-" + cleaned[1:-1]

        try:
            raw_amount_decimal = decimal.Decimal(cleaned)
        except decimal.InvalidOperation:
            return None, None, None

        # Invert sign to match system convention
        system_amount = -raw_amount_decimal

        # if system_amount <= 0:
        #     return None, None, None

        # Date
        formatted_date = parse_date(date_str=item.get("Date"))

        # Description: Type + Counterparty
        tx_type = first_non_empty(item, "Type", "Transaction Type")
        counterparty = str(item.get("Counterparty", "")).strip()

        combined_desc = f"{tx_type} {counterparty}".strip()
        norm_desc = normalize_description(combined_desc)

        return system_amount, formatted_date, norm_desc
