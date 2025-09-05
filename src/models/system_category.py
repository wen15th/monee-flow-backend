from sqlalchemy import Integer, String, DateTime, Column, Boolean
from sqlalchemy.sql import func
from .base import Base


class SystemCategory(Base):
    __tablename__ = 'system_categories'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, index=True)
    name = Column(String(255), nullable=False, server_default='')
    parent_id = Column(Integer, nullable=False, server_default='0')
    is_archived = Column(Boolean, nullable=False, server_default='false')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())