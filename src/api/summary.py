from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.user import AuthUser
from src.core.db import get_async_session
from src.core.auth import get_current_user
from src.schemas.summary import SummaryResponse
from src.services.summary import SummaryService
from datetime import date
import uuid


router = APIRouter(prefix="", tags=["summary"])


@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    min_amount_out: int = Query(0),
    max_amount_out: Optional[int] = Query(None),
    display_currency: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session),
    user: AuthUser = Depends(get_current_user),
):
    return await SummaryService.get_summary(
        db=db,
        user_id=uuid.UUID(user.user_id),
        start_date=start_date,
        end_date=end_date,
        min_amount_out=min_amount_out,
        max_amount_out=max_amount_out,
        display_currency=display_currency,
    )
