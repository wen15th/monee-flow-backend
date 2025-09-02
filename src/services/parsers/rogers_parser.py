import logging

from src.core.config import SessionLocal
from .base import BaseBankParser
from .utils import normalize_description, parse_date
from src.schemas.transaction import TransactionCreate
from src.crud.global_rule_crud import get_global_rule_by_norm_desc
from src.crud.transaction_crud import create_transactions_batch
from src.services.categorizers.llm_categorizer import HFTransactionCategorizer
import uuid
import decimal


class RogersBankParser(BaseBankParser):
    def parse(self, user_id: uuid.UUID, raw_data: list[dict]):
        transactions = []
        uncat_transactions = []
        uncat_desc_set = set()

        with SessionLocal() as db:
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
                # 1. Query from global_rules
                global_rule = get_global_rule_by_norm_desc(db, norm_desc)
                if global_rule:
                    transactions.append(TransactionCreate(
                        user_id=user_id,
                        date=formatted_date,
                        description=norm_desc,
                        category_id=global_rule.category_id,
                        category_name=global_rule.category_name,
                        amount=amount,
                        statement_id=0,
                    ))
                else:
                    uncat_transactions.append(TransactionCreate(
                        user_id=user_id,
                        date=formatted_date,
                        description=norm_desc,
                        category_id=0,
                        category_name='',
                        amount=amount,
                        statement_id=0,
                    ))
                    uncat_desc_set.add(norm_desc)

            # 2. Call LLM API
            failed_descs = []
            if uncat_desc_set:
                categorizer = HFTransactionCategorizer()
                auto_category_list = categorizer.categorize(list(uncat_desc_set))
                trans_category_dict = {item['norm_desc']: item for item in auto_category_list}
                for i in range(len(uncat_transactions)):
                    desc = uncat_transactions[i].description
                    if desc in trans_category_dict:
                        uncat_transactions[i].category_id = trans_category_dict[desc]['category_id']
                        uncat_transactions[i].category_name = trans_category_dict[desc]['category_name']
                    else:
                        failed_descs.append(desc)

            if failed_descs:
                logging.error(f"LLM categorize failed. Uncategorized transaction descriptions/merchants: {failed_descs}")

            # Save to db
            transactions += uncat_transactions
            create_transactions_batch(db, transactions)
            logging.info(f"[{self.__class__.__name__}] parse: user_id={user_id}, parsed {len(transactions)} transactions")