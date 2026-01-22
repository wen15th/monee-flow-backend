from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.exchange_rates_crud import upsert_rates_for_day

EPSILON = Decimal("0.00000001")


async def write_daily_snapshot(
    db: AsyncSession,
    *,
    timestamp: int,
    base_currency: str,
    source: str,
    rates: Dict[str, Decimal],  # quote -> rate
) -> Tuple[int, int]:
    as_of_date = datetime.fromtimestamp(timestamp, tz=timezone.utc).date()
    source_ts = datetime.fromtimestamp(timestamp, tz=timezone.utc)

    return await upsert_rates_for_day(
        db,
        as_of_date=as_of_date,
        base_currency=base_currency,
        source=source,
        source_ts=source_ts,
        rates=rates,
        epsilon=EPSILON,
    )
