from .base import BaseBankParser
from .utils import normalize_description, parse_date

import decimal


class RogersBankParser(BaseBankParser):

    def get_csv_header(self):
        return None

    def extract_transaction_fields(self, item: dict):
        # Amount
        raw_amount = str(item["Amount"]).strip()
        if raw_amount.startswith("(") and raw_amount.endswith(")"):
            return None, None, None

        cleaned = raw_amount.replace("$", "").replace(",", "")
        amount = decimal.Decimal(cleaned)

        # Date
        formatted_date = parse_date(date_str=item["Date"])

        # Normalized description
        norm_desc = normalize_description(item["Merchant Name"])
        return amount, formatted_date, norm_desc
