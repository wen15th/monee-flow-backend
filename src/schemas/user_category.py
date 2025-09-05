import decimal

from pydantic import BaseModel, ConfigDict, UUID4, Field, condecimal
from typing import Optional, List
from datetime import date, datetime


class UserCategoryCreate(BaseModel):
    user_id: UUID4
    name: str
    is_del: Optional[int] = Field(default=False)


class UserCategoryRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
