import logging
import uuid
from typing import Optional
from datetime import date
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.category_service import CategoryService
from src.services.exchange_rate_service import ExchangeRateService
from src.schemas.summary import (
    SummaryResponse,
    CategorySummary,
    MonthlySummary,
    SectionSummary,
)
from src.helpers.money import to_minor_units
from src.crud import transaction_crud as tx_crud
from decimal import Decimal


class SummaryService:
    @staticmethod
    async def get_summary(
        db: AsyncSession,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount_out: Optional[int] = None,
        max_amount_out: Optional[int] = None,
        display_currency: Optional[str] = None,
        status: Optional[int] = 1,
    ) -> SummaryResponse:

        min_amount_out_minor = (
            to_minor_units(min_amount_out) if min_amount_out is not None else None
        )
        max_amount_out_minor = (
            to_minor_units(max_amount_out) if max_amount_out is not None else None
        )

        # Get the transactions by filters
        items, total = await tx_crud.get_transactions_by_user(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            min_amount_out=min_amount_out_minor,
            max_amount_out=max_amount_out_minor,
            status=status,
            limit=None,
        )

        # Convert amounts from original currency to display_currency
        if display_currency:
            ex_rate_service = ExchangeRateService()
            display_amounts, _ = await ex_rate_service.convert_transaction_amounts(
                db=db, transactions=items, display_currency=display_currency
            )
        else:
            display_amounts = [tx.amount for tx in items]

        # Total expenses
        total_expenses: Decimal = sum(display_amounts, Decimal(0))

        # Get category names: category_id => category_name
        cat_service = CategoryService()
        cat_id_name_map = await cat_service.get_category_id_name_map(
            db=db, category_ids=[tx.category_id for tx in items]
        )

        # Build dicts by category and month
        category_totals = defaultdict(int)
        monthly_totals = defaultdict(int)

        for i, tx in enumerate(items):
            # Category -> amount
            category_totals[cat_id_name_map[tx.category_id]] += display_amounts[i]
            # Month -> amount
            month_str = tx.tx_date.strftime("%Y-%m")
            monthly_totals[month_str] += display_amounts[i]

        # Build category expense list
        category_expenses = [
            CategorySummary(
                category=cat,
                amount=amt,
                percentage=(
                    round(float(amt / total_expenses * 100), 1)
                    if total_expenses > 0
                    else 0.0
                ),
            )
            for cat, amt in category_totals.items()
        ]

        # Build monthly expense list
        monthly_expenses = [
            MonthlySummary(month=m, amount=amt) for m, amt in monthly_totals.items()
        ]
        # Sort by month
        monthly_expenses.sort(key=lambda x: x.month)

        return SummaryResponse(
            expenses=SectionSummary(
                total=float(total_expenses),
                categories=category_expenses,
                monthly=monthly_expenses,
            ),
            incomes=None,
            display_currency=display_currency,
        )
