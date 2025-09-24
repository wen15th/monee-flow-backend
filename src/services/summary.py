import logging
import uuid
from typing import Optional
from datetime import date

from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.summary import (
    SummaryResponse,
    CategorySummary,
    MonthlySummary,
    SectionSummary,
)
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
    ) -> SummaryResponse:
        # Get the transactions by filters
        items, total = await tx_crud.get_transactions_by_user(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            min_amount_out=min_amount_out,
            max_amount_out=max_amount_out,
            limit=None,
        )

        # Total expenses
        total_expenses: Decimal = sum((tx.amount for tx in items), Decimal(0))

        # Build dicts by category and month
        category_totals = defaultdict(Decimal)
        monthly_totals = defaultdict(Decimal)
        for tx in items:
            # Category -> amount
            category_totals[tx.category_name] += tx.amount
            # Month -> amount
            month_str = tx.date.strftime("%Y-%m")
            monthly_totals[month_str] += tx.amount

        # Build category expense list
        category_expenses = [
            CategorySummary(
                category=cat,
                amount=float(amt),
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
            MonthlySummary(month=m, amount=float(amt))
            for m, amt in monthly_totals.items()
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
            currency="CAD",
        )
