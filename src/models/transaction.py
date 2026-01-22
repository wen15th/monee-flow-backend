from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Date,
    SmallInteger,
    ForeignKey,
    DateTime,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tx_date = Column(Date, nullable=False)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False)
    category_id = Column(Integer, nullable=False, server_default="0")
    description = Column(String(255), nullable=False, server_default="")
    statement_id = Column(BigInteger, nullable=True, index=True)
    status = Column(SmallInteger, nullable=False, server_default="1")
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
        Index("idx_transactions_user_currency_amount", "user_id", "currency", "amount"),
        Index(
            "idx_transactions_user_currency_txdate", "user_id", "currency", "tx_date"
        ),
        Index("idx_transactions_user_txdate", "user_id", "tx_date"),
        CheckConstraint("currency ~ '^[A-Z]{3}$'", name="chk_currency_iso4217"),
        CheckConstraint("status IN (1,2)", name="chk_status_valid"),
    )
