import decimal

from pydantic import BaseModel, ConfigDict, UUID4, Field, condecimal
from typing import Optional, List
from datetime import date, datetime


class UserSysCategoryCreate(BaseModel):
    user_id: UUID4
    category_id: Optional[int] = 0
    is_enabled: Optional[int] = Field(default=True)


class UserSysCategoryRead(BaseModel):
    id: int
    user_id: UUID4
    category_id: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
