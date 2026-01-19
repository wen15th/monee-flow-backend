import uuid
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.common import PaginatedResponse
from src.schemas.transaction import TransactionRead, TransactionUpdate
from src.services.category_service import CategoryService
from src.crud import transaction_crud
from datetime import date
from typing import Optional


class TransactionService:
    @staticmethod
    async def get_user_transactions(
        db: AsyncSession,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount_out: Optional[int] = None,
        max_amount_out: Optional[int] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[TransactionRead]:
        """Fetch user transactions with pagination and optional date filtering."""
        skip = (page - 1) * page_size
        items, total = await transaction_crud.get_transactions_by_user(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            min_amount_out=min_amount_out,
            max_amount_out=max_amount_out,
            skip=skip,
            limit=page_size,
        )

        return PaginatedResponse[TransactionRead](
            items=[TransactionRead.model_validate(tx) for tx in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    async def update_transaction(
        db: AsyncSession,
        transaction_id: int,
        user_id: uuid.UUID,
        tx_update: TransactionUpdate,
    ):
        db_obj = await transaction_crud.get_transaction_by_id(db, transaction_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if db_obj.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this transaction"
            )

        # Verify category
        category_service = CategoryService(str(user_id))
        await category_service.check_user_category(
            db=db, category_id=db_obj.category_id
        )

        return await transaction_crud.update_transaction(db, db_obj, tx_update)
