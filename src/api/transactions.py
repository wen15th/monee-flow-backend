from src.core.auth import get_current_user
from src.schemas.user import AuthUser
from src.core.db import get_async_session
from src.schemas.transaction import TransactionRead, TransactionUpdate
from src.schemas.common import PaginatedResponse
from src.services.transaction_service import TransactionService
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi import Depends, Query, APIRouter
from datetime import date
import uuid

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=PaginatedResponse[TransactionRead])
async def get_transactions(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    min_amount_out: int = Query(0),
    max_amount_out: Optional[int] = Query(None),
    display_currency: Optional[str] = Query(None),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    user: AuthUser = Depends(get_current_user),
):
    return await TransactionService.get_user_transactions(
        db=db,
        user_id=uuid.UUID(user.user_id),
        start_date=start_date,
        end_date=end_date,
        min_amount_out=min_amount_out,
        max_amount_out=max_amount_out,
        display_currency=display_currency,
        page=page,
        page_size=page_size,
    )


@router.patch("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: int,
    tx_update: TransactionUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: AuthUser = Depends(get_current_user),
):
    return await TransactionService.update_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=uuid.UUID(user.user_id),
        tx_update=tx_update,
    )
