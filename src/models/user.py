import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,  # python default
        server_default=text("gen_random_uuid()"),  # db default
        index=True,
    )
    first_name = Column(String(100), nullable=False, server_default="")
    last_name = Column(String(100), nullable=False, server_default="")
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False, server_default="")
    default_display_currency = Column(String(3), nullable=False, server_default="USD")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
