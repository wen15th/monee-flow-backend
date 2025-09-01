from src.core.app_context import AppContext
from .base import BaseBankParser
from .utils import normalize_description, parse_date
from src.schemas.transaction import TransactionCreate
from src.crud.global_rule_crud import get_global_rule_by_norm_desc
import uuid
import decimal

class RogersBankParser(BaseBankParser):
    def parse(self, user_id: uuid.UUID, raw_data: list[dict], ctx: AppContext) -> list[TransactionCreate]:
        transactions = []
        desc_set = set()

        for item in raw_data:
            raw_amount = str(item['Amount']).strip()
            if raw_amount.startswith("(") and raw_amount.endswith(")"):
                continue
            cleaned = raw_amount.replace("$", "").replace(",", "")
            amount = decimal.Decimal(cleaned)

            # Date
            formatted_date = parse_date(date_str=item['Date'])

            # Transaction Description
            norm_desc = normalize_description(item['Merchant Name'])

            # Categorize transaction
            category_id = 12
            category_name = 'Other'
            # 1. Query from global_rules
            global_rule = get_global_rule_by_norm_desc(ctx.db, norm_desc)
            if global_rule:
                category_id = global_rule.category_id
                category_name = global_rule.category_name
                transactions.append(TransactionCreate(
                    user_id=user_id,
                    date=formatted_date,
                    description=norm_desc,
                    category_id=category_id,  # To be parsed
                    category_name=category_name,  # To be parsed
                    amount=amount,
                    statement_id=0,
                ))
            else:
                desc_set.add(norm_desc)

        print(desc_set)
        # TODO: 2. Call LLM API
        # [category_id, category_name] = categorize_transaction()

        return transactions
