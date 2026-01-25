from pydantic import BaseModel
from typing import Optional, List


class CategorySummary(BaseModel):
    category: str
    amount: int
    percentage: float


class MonthlySummary(BaseModel):
    month: str
    amount: int


class SectionSummary(BaseModel):
    total: float
    categories: List[CategorySummary]
    monthly: List[MonthlySummary]


class SummaryResponse(BaseModel):
    expenses: SectionSummary
    incomes: Optional[SectionSummary] = None
    display_currency: Optional[str] = "USD"
