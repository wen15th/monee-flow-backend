from sqlalchemy import Integer, String, DateTime, Column, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base


class UserCategoryPref(Base):
    __tablename__ = 'user_category_prefs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, nullable=False, server_default='0')
    parent_id = Column(Integer, nullable=False, server_default='0')
    display_name = Column(String(100), nullable=False, server_default='')
    is_enabled = Column(Boolean, nullable=False, server_default='true')
    sort_order = Column(Integer, nullable=False, server_default='0')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_user_enabled", "user_id", "is_enabled"),
    )