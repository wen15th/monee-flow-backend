from sqlalchemy import Integer, String, DateTime, Column, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base


class UserCategory(Base):
    __tablename__ = "user_categories"

    id = Column(
        Integer, primary_key=True, nullable=False, autoincrement=True, index=True
    )
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False, server_default="")
    is_del = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
