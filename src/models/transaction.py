from sqlalchemy import Column, Integer, BigInteger, String, Date, DECIMAL, SmallInteger, ForeignKey, DateTime, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, server_default='1970-01-01')
    description = Column(String(255), nullable=False, server_default='')
    category_id = Column(Integer, nullable=False, server_default='0')
    category_name = Column(String(255), nullable=False, server_default='')
    amount = Column(DECIMAL(10, 2), nullable=False)
    statement_id = Column(BigInteger, nullable=False, index=True, server_default='0')
    status = Column(SmallInteger, nullable=False, server_default='1')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_transactions_user_id", "user_id"),
        Index("idx_transactions_statement_id", "statement_id"),
        CheckConstraint("status IN (1,2,3)", name="chk_status_valid"),
    )
