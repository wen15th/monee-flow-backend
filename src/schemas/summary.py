from pydantic import BaseModel
from typing import Optional, List


class CategorySummary(BaseModel):
    category: str
    amount: float
    percentage: float


class MonthlySummary(BaseModel):
    month: str
    amount: float


class SectionSummary(BaseModel):
    total: float
    categories: List[CategorySummary]
    monthly: List[MonthlySummary]


class SummaryResponse(BaseModel):
    expenses: SectionSummary
    incomes: Optional[SectionSummary] = None
    currency: Optional[str] = "CAD"
