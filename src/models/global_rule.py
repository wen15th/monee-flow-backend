from sqlalchemy import Integer, String, DateTime, Column, Boolean, Text
from sqlalchemy.sql import func
from .base import Base


class GlobalRule(Base):
    __tablename__ = 'global_rules'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, index=True)
    norm_desc = Column(Text, nullable=False, server_default='')
    category_id = Column(Integer, nullable=False, server_default='0')
    category_name = Column(String(255), nullable=False, server_default='')
    note = Column(Text, nullable=False, server_default='')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())