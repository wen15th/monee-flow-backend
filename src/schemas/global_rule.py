from pydantic import BaseModel, ConfigDict, UUID4, Field, condecimal
from datetime import datetime


class GlobalRuleCreate(BaseModel):
    norm_desc: str
    category_id: int
    category_name: str
    note: str

class GlobalRuleRead(BaseModel):
    id: int
    norm_desc: str
    category_id: int
    category_name: str
    note: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
