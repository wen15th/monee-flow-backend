from sqlalchemy import Column, BigInteger, SmallInteger, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base

class Statement(Base):
    __tablename__ = "statements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    s3_key = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False, server_default='1970-01-01 00:00:00')
    end_time = Column(DateTime, nullable=False, server_default='1970-01-01 00:00:00')
    source = Column(String(50), nullable=True)  # TD, BMO, Rogers, etc.
    status = Column(SmallInteger, nullable=False, server_default='1')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_statements_user_id", "user_id"),
    )
