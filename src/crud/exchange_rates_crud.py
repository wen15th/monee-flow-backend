from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Tuple, Set
from sqlalchemy import desc, distinct, func, select, literal
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.exchange_rate import ExchangeRate


class FxRateNotFound(Exception):
    pass


async def get_rates_by_date(
    db: AsyncSession,
    *,
    as_of_date: date,
    base_currency: str,
    source: str,
    quote_currencies: Iterable[str],
) -> Dict[str, ExchangeRate]:
    quotes = [q.upper() for q in set(quote_currencies) if q]
    if not quotes:
        return {}

    stmt = (
        select(ExchangeRate)
        .where(ExchangeRate.as_of_date == as_of_date)
        .where(ExchangeRate.base_currency == base_currency)
        .where(ExchangeRate.source == source)
        .where(ExchangeRate.quote_currency.in_(quotes))
    )
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return {row.quote_currency: row for row in rows}


async def get_best_rate_date(
    db: AsyncSession,
    *,
    tx_date: date,
    base_currency: str,
    source: str,
    required_quotes: Iterable[str],
) -> date:
    """
    Rules:
    1) Use tx_date if that day has ALL required quotes.
    2) Else use the latest day <= tx_date that has ALL required quotes.
    3) If nothing exists on/before tx_date, use the latest day in the table
       that has ALL required quotes.
    """
    quotes: Set[str] = {q.upper() for q in required_quotes if q}
    if not quotes:
        return tx_date

    # 1) exact day check (cheap and keeps semantics simple)
    exact = await get_rates_by_date(
        db,
        as_of_date=tx_date,
        base_currency=base_currency,
        source=source,
        quote_currencies=quotes,
    )
    if len(exact) == len(quotes):
        return tx_date

    async def _find_latest_date(*, le_date: Optional[date]) -> Optional[date]:
        stmt = (
            select(ExchangeRate.as_of_date)
            .where(ExchangeRate.base_currency == base_currency)
            .where(ExchangeRate.source == source)
            .where(ExchangeRate.quote_currency.in_(list(quotes)))
        )
        if le_date is not None:
            stmt = stmt.where(ExchangeRate.as_of_date <= le_date)

        stmt = (
            stmt.group_by(ExchangeRate.as_of_date)
            .having(func.count(distinct(ExchangeRate.quote_currency)) == len(quotes))  # type: ignore[arg-type]
            .order_by(desc(ExchangeRate.as_of_date))
            .limit(1)
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    # 2) latest <= tx_date
    best = await _find_latest_date(le_date=tx_date)
    if best is not None:
        return best

    # 3) latest overall
    latest = await _find_latest_date(le_date=None)
    if latest is not None:
        return latest

    raise FxRateNotFound(
        f"No FX rate day found that covers quotes={sorted(quotes)} "
        f"for base={base_currency} source={source}"
    )


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
