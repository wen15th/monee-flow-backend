from datetime import datetime, timezone, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Tuple, Set, List, Sequence, Optional

from black.trans import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.exchange_rates_crud import (
    get_best_rate_date,
    get_rates_by_date,
    upsert_rates_for_day,
)
from src.models.exchange_rate import ExchangeRate


class ExchangeRateService:
    BASE_CURRENCY = "USD"
    SOURCE = "openexchangerates"
    EPSILON = Decimal("0.00000001")

    @classmethod
    async def convert(
        cls,
        db: AsyncSession,
        *,
        from_currency: str,
        to_currency: str,
        tx_date: date,
        amounts: List[int],  # minor units
    ) -> tuple[List[int], date]:
        """
        Convert amount (minor units) from one currency to another.

        Returns:
            (converted_amounts, rate_date_used)
        """
        from_cur = from_currency.upper()
        to_cur = to_currency.upper()

        if from_cur == to_cur:
            return amounts, tx_date

        # Quotes that need to be converted
        required_quotes: Set[str] = set()
        if from_cur != cls.BASE_CURRENCY:
            required_quotes.add(from_cur)
        if to_cur != cls.BASE_CURRENCY:
            required_quotes.add(to_cur)

        # Find the rate date that can be used
        rate_date = await get_best_rate_date(
            db,
            tx_date=tx_date,
            base_currency=cls.BASE_CURRENCY,
            source=cls.SOURCE,
            required_quotes=required_quotes,
        )

        # Fetch rates in that day
        rates: Dict[str, ExchangeRate] = await get_rates_by_date(
            db,
            as_of_date=rate_date,
            base_currency=cls.BASE_CURRENCY,
            source=cls.SOURCE,
            quote_currencies=required_quotes,
        )

        # Safety check (should not fail if the get_best_rate_date is correct)
        if len(rates) != len(required_quotes):
            missing = required_quotes - set(rates.keys())
            raise ValueError(
                f"Missing FX rates for {sorted(missing)} "
                f"on {rate_date} base={cls.BASE_CURRENCY}"
            )

        converted_amounts = []
        for amount in amounts:
            if amount == 0:
                converted_amounts.append(0)
                continue

            # Conversion
            amt = Decimal(amount)

            if from_cur == cls.BASE_CURRENCY:
                # USD -> to
                rate_to = Decimal(rates[to_cur].rate)
                result = amt * rate_to

            elif to_cur == cls.BASE_CURRENCY:
                # from -> USD
                rate_from = Decimal(rates[from_cur].rate)
                result = amt / rate_from

            else:
                # from -> USD -> to
                rate_from = Decimal(rates[from_cur].rate)
                rate_to = Decimal(rates[to_cur].rate)
                result = amt * rate_to / rate_from

            # Rounding to minor units
            converted = int(result.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            converted_amounts.append(converted)

        return converted_amounts, rate_date

    @classmethod
    async def convert_transaction_amounts(
        cls,
        db: AsyncSession,
        *,
        transactions: Sequence[object],  # list of tx ORM objects
        display_currency: Optional[str] = None,
    ) -> tuple[list[int], list[date]]:
        """
        Convert tx.amount (minor units) for each item into display_currency (minor units).

        Assumptions:
          - each item has attributes: currency (str), tx_date (date), amount (int)
          - amount is minor units in item's currency

        Returns:
          (display_amounts, rate_dates_used) aligned with items by index
        """

        n = len(transactions)
        display_amounts: list[Optional[int]] = [None] * n
        rate_dates_used: list[Optional[date]] = [None] * n

        # tuple[from_currency, to_currency, tx_date] -> list[tuple[idx, amount]]
        buckets: dict[tuple[str, str, date], list[tuple[int, int]]] = defaultdict(list)
        for i, tx in enumerate(transactions):
            from_cur = tx.currency.upper()
            tx_date = tx.tx_date
            buckets[(from_cur, display_currency, tx_date)].append((i, tx.amount))

        for (from_cur, to_cur, tx_date), idx_amount_list in buckets.items():
            amounts = [amount for _, amount in idx_amount_list]

            converted, rate_date_used = await cls.convert(
                db,
                from_currency=from_cur,
                to_currency=to_cur,
                tx_date=tx_date,
                amounts=amounts,
            )

            for (idx, _), conv_amt in zip(idx_amount_list, converted, strict=True):
                display_amounts[idx] = conv_amt
                rate_dates_used[idx] = rate_date_used

        return display_amounts, rate_dates_used

    async def write_daily_snapshot(
        self,
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
            epsilon=self.EPSILON,
        )
