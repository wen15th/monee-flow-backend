from pydantic import BaseModel, ConfigDict, Field, condecimal
from typing import List
from datetime import date, datetime


class ExchangeRateCreate(BaseModel):
    as_of_date: date
    base_currency: str = Field(pattern=r"^[A-Z]{3}$")
    quote_currency: str = Field(pattern=r"^[A-Z]{3}$")
    rate: condecimal(max_digits=18, decimal_places=8)
    source: str = Field(min_length=1, max_length=100)
    source_ts: datetime


class ExchangeRateRead(BaseModel):
    id: int
    as_of_date: date
    base_currency: str
    quote_currency: str
    rate: condecimal(max_digits=18, decimal_places=8)
    source: str
    source_ts: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExchangeRateList(BaseModel):
    items: List[ExchangeRateRead]
