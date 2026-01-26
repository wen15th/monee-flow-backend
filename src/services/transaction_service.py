import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.common import PaginatedResponse
from src.schemas.transaction import TransactionRead, TransactionUpdate
from src.services.category_service import CategoryService
from src.services.exchange_rate_service import ExchangeRateService
from src.helpers.money import to_minor_units
from src.crud import transaction_crud
from datetime import date
from typing import Optional, List


class TransactionService:
    @staticmethod
    async def get_user_transactions(
        db: AsyncSession,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount_out: Optional[int] = None,
        max_amount_out: Optional[int] = None,
        display_currency: Optional[str] = None,
        status: Optional[int] = 1,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[TransactionRead]:
        """Fetch user transactions with pagination and optional date filtering."""

        min_amount_out_minor = (
            to_minor_units(min_amount_out) if min_amount_out is not None else None
        )
        max_amount_out_minor = (
            to_minor_units(max_amount_out) if max_amount_out is not None else None
        )

        skip = (page - 1) * page_size
        items, total = await transaction_crud.get_transactions_by_user(
            db=db,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            min_amount_out=min_amount_out_minor,
            max_amount_out=max_amount_out_minor,
            status=status,
            skip=skip,
            limit=page_size,
        )

        # Get category_name for each item
        cat_service = CategoryService()
        cat_id_name_map = await cat_service.get_category_id_name_map(
            db=db, category_ids=[tx.category_id for tx in items]
        )
        for tx in items:
            tx.category_name = cat_id_name_map[tx.category_id]

        # Currency conversion
        if display_currency is None:
            out: List[TransactionRead] = []
            for i, tx in enumerate(items):
                dto = TransactionRead.model_validate(tx)
                dto.converted_amount = dto.amount
                dto.display_currency = dto.currency
                out.append(dto)
            return PaginatedResponse[TransactionRead](
                items=out,
                total=total,
                page=page,
                page_size=page_size,
            )

        # Convert transaction amounts from original currency to display_currency
        ex_rate_service = ExchangeRateService()
        display_amounts, rate_dates_used = (
            await ex_rate_service.convert_transaction_amounts(
                db, transactions=items, display_currency=display_currency
            )
        )

        # Build response DTOs
        out: List[TransactionRead] = []
        for i, tx in enumerate(items):
            dto = TransactionRead.model_validate(tx)
            dto.display_currency = display_currency
            dto.converted_amount = display_amounts[i]
            dto.rate_date_used = rate_dates_used[i]
            out.append(dto)

        return PaginatedResponse[TransactionRead](
            items=out,
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
