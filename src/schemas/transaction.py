import decimal

from pydantic import BaseModel, ConfigDict, UUID4, Field, condecimal
from typing import Optional
from datetime import date, datetime


class TransactionCreate(BaseModel):
    user_id: UUID4
    statement_id: int
    transaction_date: date
    posted_date: date
    merchant_name: str
    merchant_category: str
    customized_category: str
    amount: condecimal(max_digits=10, decimal_places=2)
    status: Optional[int] = Field(default=1)


class TransactionRead(BaseModel):
    id: int
    user_id: UUID4
    statement_id: int
    transaction_date: date
    posted_date: date
    merchant_name: str
    merchant_category: str
    customized_category: str
    amount: condecimal(max_digits=10, decimal_places=2)
    status: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
