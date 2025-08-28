from pydantic import BaseModel, ConfigDict, UUID4, Field
from typing import Optional
from datetime import datetime


class StatementCreate(BaseModel):
    user_id: UUID4
    s3_key: str
    start_time: datetime
    end_time: datetime
    source: str = Field(default='')
    status: Optional[int] = Field(default=1)


class StatementRead(BaseModel):
    id: int
    user_id: UUID4
    s3_key: str
    start_time: datetime
    end_time: datetime
    source: Optional[str]
    status: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
