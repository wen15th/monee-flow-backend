import io
import logging
import uuid
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
from src.core.db import SessionLocal
from src.core import s3
from src.schemas.transaction import TransactionCreate
from src.schemas.global_rule import GlobalRuleCreate
from src.crud.global_rule_crud import (
    get_global_rule_by_norm_desc,
    create_global_rules_batch,
)
from src.crud.transaction_crud import create_transactions_batch, get_transactions_for_dedup
from src.services.categorizers.llm_categorizer import LLMTransactionCategorizer


class BaseBankParser:
    def parse(self, user_id: uuid.UUID, stmt_id: int, currency: str, file_path: str):
        # Download from S3 and read
        header = self.get_csv_header()
        content = s3.download_file(file_path)
        df = pd.read_csv(io.BytesIO(content), header=None if header else "infer", names=header)
        df = df.fillna("")
        raw_data = df.to_dict(orient="records")

        transactions = []
        uncat_transactions = []
        uncat_desc_set = set()

        with SessionLocal() as db:
            for item in raw_data:
                # Call subclass.extract_transaction_fields to extract columns
                amount, formatted_date, norm_desc = self.extract_transaction_fields(
                    item
                )
                # TODO: Save income too
                if amount is None or amount < 0:
                    continue

                amount_minor = int(
                    (amount * Decimal("100")).quantize(
                        Decimal("1"), rounding=ROUND_HALF_UP
                    )
                )
                # 1. Check global rules
                global_rule = get_global_rule_by_norm_desc(db, norm_desc)
                if global_rule:
                    transactions.append(
                        TransactionCreate(
                            user_id=user_id,
                            tx_date=formatted_date,
                            description=norm_desc,
                            category_id=global_rule.category_id,
                            amount=amount_minor,
                            currency=currency,
                            statement_id=stmt_id,
                        )
                    )
                else:
                    uncat_transactions.append(
                        TransactionCreate(
                            user_id=user_id,
                            tx_date=formatted_date,
                            description=norm_desc,
                            category_id=0,
                            amount=amount_minor,
                            currency=currency,
                            statement_id=stmt_id,
                        )
                    )
                    uncat_desc_set.add(norm_desc)

            # 2. Call LLM for uncategorized
            failed_descs = []
            if uncat_desc_set:
                categorizer = LLMTransactionCategorizer()
                auto_category_list = categorizer.categorize(list(uncat_desc_set))

                new_global_rules = [GlobalRuleCreate(**d) for d in auto_category_list]
                trans_category_dict = {d["norm_desc"]: d for d in auto_category_list}

                for t in uncat_transactions:
                    if t.description in trans_category_dict:
                        cat = trans_category_dict[t.description]
                        t.category_id = cat["category_id"]
                    else:
                        failed_descs.append(t.description)

                create_global_rules_batch(db, new_global_rules)
                logging.info(
                    f"[{self.__class__.__name__}] saved new global rules: {new_global_rules}"
                )

            if failed_descs:
                logging.error(f"LLM categorize failed: {failed_descs}")

            # 3. Dedup detection: mark transactions that match existing DB records
            transactions += uncat_transactions
            new_dates = {t.tx_date for t in transactions}
            existing = get_transactions_for_dedup(db, user_id, new_dates)
            # Build lookup: (tx_date, amount, currency, description) -> earliest existing id
            existing_lookup: dict = {}
            for ex in existing:
                key = (ex.tx_date, ex.amount, ex.currency, ex.description)
                if key not in existing_lookup or ex.id < existing_lookup[key]:
                    existing_lookup[key] = ex.id

            for t in transactions:
                key = (t.tx_date, t.amount, t.currency, t.description)
                if key in existing_lookup:
                    t.status = 3
                    t.duplicate_of_id = existing_lookup[key]

            # 4. Save all transactions
            create_transactions_batch(db, transactions)
            logging.info(
                f"[{self.__class__.__name__}] user_id={user_id}, parsed {len(transactions)} transactions"
            )

    def get_csv_header(self):
        """Get csv header from different banks."""
        raise NotImplementedError

    def extract_transaction_fields(self, raw_item: dict):
        """Subclass must implement and return (amount, formatted_date, norm_desc)."""
        raise NotImplementedError
