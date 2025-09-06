from pydantic import BaseModel, ConfigDict, UUID4, Field, condecimal
from typing import Optional, List
from datetime import date, datetime


class TransactionCreate(BaseModel):
    user_id: UUID4
    date: date
    description: str
    category_id: Optional[int] = 0
    category_name: Optional[str] = ""
    amount: condecimal(max_digits=10, decimal_places=2)
    statement_id: Optional[int] = 0
    status: Optional[int] = Field(default=1)


class TransactionRead(BaseModel):
    id: int
    user_id: UUID4
    date: date
    description: str
    category_id: int
    category_name: str
    amount: condecimal(max_digits=10, decimal_places=2)
    statement_id: int
    status: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionCategory(BaseModel):
    norm_desc: str
    category_id: int
    category_name: str
    note: str


class TransactionCategoryList(BaseModel):
    trans_category_list: List[TransactionCategory]


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    amount: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    status: Optional[int] = None
