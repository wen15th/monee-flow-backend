import asyncio
import httpx
import logging
from src.core.config import OER_APP_ID, OER_BASE_URL
from src.core.db import AsyncSessionLocal
from src.services.exchange_rate_service import write_daily_snapshot
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger("exchange_rates_job")

AVAILABLE_CURRENCIES = ["CAD", "CNY"]


@dataclass(frozen=True)
class OERLatestResponse:
    timestamp: int
    base: str
    rates: Dict[str, Decimal]


class ExchangeRatesJobError(RuntimeError):
    pass


async def fetch_oer_latest(
    client: httpx.AsyncClient,
    *,
    timeout: float = 10.0,
    max_retries: int = 3,
) -> OERLatestResponse:
    if not OER_APP_ID:
        raise ExchangeRatesJobError("OER APP_ID is empty")

    params = {"app_id": OER_APP_ID, "symbols": ",".join(AVAILABLE_CURRENCIES)}
    last_exception: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            res = await client.get(OER_BASE_URL, params=params, timeout=timeout)
            res.raise_for_status()
            payload = res.json()

            ts = int(payload["timestamp"])
            base = str(payload.get("base", "USD"))
            rates = {
                ccy: Decimal(str(payload["rates"][ccy])) for ccy in AVAILABLE_CURRENCIES
            }

            return OERLatestResponse(timestamp=ts, base=base, rates=rates)

        except (httpx.TimeoutException, httpx.HTTPError, KeyError, ValueError) as e:
            last_exception = e
            # If status is 4xx, then it probably params / app_id issue, no need to retry
            # Except for 429: Too Many Requests
            status = getattr(getattr(e, "response", None), "status_code", None)
            if isinstance(e, httpx.HTTPStatusError) and status is not None:
                if 400 <= status < 500 and status != 429:
                    raise ExchangeRatesJobError(
                        f"OER request failed: HTTP {status}"
                    ) from e

            # Exponential Backoff: 1,2,4,8...
            backoff = 2 ** (attempt - 1)
            await asyncio.sleep(backoff)

    raise ExchangeRatesJobError("OER request failed after retries") from last_exception


async def main():
    # Pull the latest rates
    async with httpx.AsyncClient() as client:
        res = await fetch_oer_latest(client)

    # Write daily snapshot
    async with AsyncSessionLocal() as db:
        try:
            inserted, updated = await write_daily_snapshot(
                db,
                timestamp=res.timestamp,
                base_currency=res.base,
                source="openexchangerates",
                rates=res.rates,
            )
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("exchange rates job failed during db transaction")
            raise

    logger.info(
        "as_of_date=%s base=%s inserted=%s updated=%s",
        datetime.fromtimestamp(res.timestamp, tz=timezone.utc).date(),
        res.base,
        inserted,
        updated,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    asyncio.run(main())
