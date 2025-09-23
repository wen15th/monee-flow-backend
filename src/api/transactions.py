from src.core.auth import get_current_user
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
    user_id: uuid.UUID,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
):
    return await TransactionService.get_user_transactions(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@router.patch("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: int,
    user_id: uuid.UUID,
    tx_update: TransactionUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    return await TransactionService.update_transaction(
        db=db, transaction_id=transaction_id, user_id=user_id, tx_update=tx_update
    )
