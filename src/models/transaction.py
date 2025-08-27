from sqlalchemy import Column, BigInteger, String, Date, DECIMAL, SmallInteger, ForeignKey, DateTime, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    statement_id = Column(BigInteger, ForeignKey("statements.id"), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, server_default='1970-01-01')
    posted_date = Column(Date, nullable=False, server_default='1970-01-01')
    merchant_name = Column(String(255), nullable=True)
    merchant_category = Column(String(255), nullable=True)
    customized_category = Column(String(255), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(SmallInteger, nullable=False, server_default='1')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_transactions_user_id", "user_id"),
        Index("idx_transactions_statement_id", "statement_id"),
        CheckConstraint("status IN (1,2,3)", name="chk_status_valid"),
    )
