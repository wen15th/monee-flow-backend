from decimal import Decimal, ROUND_HALF_UP

_MINOR_FACTOR = Decimal("100")


def to_minor_units(amount: Decimal | int) -> int:
    """
    Convert a Decimal amount in major units (e.g. dollars) to minor units (e.g. cents).

    Uses ROUND_HALF_UP for financial rounding.
    """
    return int((amount * _MINOR_FACTOR).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
