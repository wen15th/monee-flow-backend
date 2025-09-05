import decimal

from pydantic import BaseModel, ConfigDict, UUID4, Field, condecimal
from typing import Optional, List
from datetime import date, datetime


class SystemCategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = 0
    is_archived: Optional[int] = Field(default=1)


class SystemCategoryRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
