import pandas as pd

from .base import BaseBankParser
from .utils import normalize_description, parse_date


class TDBankParser(BaseBankParser):
    def get_csv_header(self):
        return ["Date", "Transaction Description", "Debit", "Credit", "Balance"]

    def extract_transaction_fields(self, item: dict):
        # Amount
        amount = item["Debit"]
        if amount is None or pd.isna(amount):
            return None, None, None
        # Date
        formatted_date = parse_date(date_str=item["Date"])
        # Transaction Description
        norm_desc = normalize_description(item["Transaction Description"])

        return amount, formatted_date, norm_desc
