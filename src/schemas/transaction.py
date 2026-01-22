from pydantic import BaseModel, ConfigDict, UUID4, Field
from typing import Optional, List
from datetime import date, datetime


class TransactionCreate(BaseModel):
    user_id: UUID4
    tx_date: date
    amount: int
    currency: str
    category_id: Optional[int] = 0
    description: str
    statement_id: Optional[int] = 0
    status: Optional[int] = Field(default=1)


class TransactionRead(BaseModel):
    id: int
    user_id: UUID4
    tx_date: date
    amount: int
    currency: str
    category_id: int
    description: str
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
    tx_date: Optional[date] = None
    category_id: Optional[int] = None
    amount: Optional[int] = None
    status: Optional[int] = None
