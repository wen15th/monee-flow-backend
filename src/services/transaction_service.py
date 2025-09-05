import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.common import PaginatedResponse
from src.schemas.transaction import TransactionRead
from src.crud.transaction_crud import get_transactions_by_user
from datetime import date
from typing import Optional


class TransactionService:
    @staticmethod
    async def get_user_transactions(
        db: AsyncSession,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[TransactionRead]:
        """Fetch user transactions with pagination and optional date filtering."""
        skip = (page - 1) * page_size
        items, total = await get_transactions_by_user(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=page_size,
        )

        return PaginatedResponse[TransactionRead](
            items=[TransactionRead.model_validate(tx) for tx in items],
            total=total,
            page=page,
            page_size=page_size,
        )
