from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.exchange_rate import ExchangeRate


async def get_rates_for_day(
    db: AsyncSession,
    *,
    as_of_date: date,
    base_currency: str,
    quote_currencies: Iterable[str],
) -> Dict[str, ExchangeRate]:
    quotes = list(set(quote_currencies))
    if not quotes:
        return {}

    stmt = (
        select(ExchangeRate)
        .where(ExchangeRate.as_of_date == as_of_date)
        .where(ExchangeRate.base_currency == base_currency)
        .where(ExchangeRate.quote_currency.in_(quotes))
    )
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return {row.quote_currency: row for row in rows}


async def upsert_rates_for_day(
    db: AsyncSession,
    *,
    as_of_date: date,
    base_currency: str,
    source: str,
    source_ts: datetime,
    rates: Dict[str, Decimal],  # quote -> rate
    epsilon: Decimal,
) -> Tuple[int, int]:
    """
    Idempotent upsert (The same day and the same currency pair, upsert if not exists)
    Return (inserted_count, updated_count)
    """
    existing = await get_rates_for_day(
        db,
        as_of_date=as_of_date,
        base_currency=base_currency,
        quote_currencies=rates.keys(),
    )

    inserted = 0
    updated = 0

    for quote, new_rate in rates.items():
        row = existing.get(quote)
        if row is None:
            db.add(
                ExchangeRate(
                    as_of_date=as_of_date,
                    base_currency=base_currency,
                    quote_currency=quote,
                    rate=new_rate,
                    source=source,
                    source_ts=source_ts,
                )
            )
            inserted += 1
        else:
            old_rate = Decimal(row.rate)
            if (new_rate - old_rate).copy_abs() > epsilon:
                row.rate = new_rate
                row.source = source
                row.source_ts = source_ts
                updated += 1

    return inserted, updated
