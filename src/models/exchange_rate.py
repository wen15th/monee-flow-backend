from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    Date,
    DECIMAL,
    UniqueConstraint,
    Index,
    CheckConstraint,
)
from sqlalchemy.sql import func
from .base import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    as_of_date = Column(Date, nullable=False)
    base_currency = Column(String(3), nullable=False)
    quote_currency = Column(String(3), nullable=False)
    rate = Column(DECIMAL(18, 8), nullable=False)
    source = Column(String(100), nullable=False)
    source_ts = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "as_of_date",
            "base_currency",
            "quote_currency",
            name="ux_exchange_rates_day_pair",
        ),
        CheckConstraint(
            "base_currency ~ '^[A-Z]{3}$'", name="chk_base_currency_iso4217"
        ),
        CheckConstraint(
            "quote_currency ~ '^[A-Z]{3}$'", name="chk_quote_currency_iso4217"
        ),
    )
