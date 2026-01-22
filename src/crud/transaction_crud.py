from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional, List

from src.models import Transaction
from src.schemas.transaction import TransactionCreate, TransactionUpdate
from datetime import date
import uuid


def create_transaction(db: Session, transaction_data: TransactionCreate) -> Transaction:
    transaction_data_dict = transaction_data.model_dump(exclude_unset=True)
    new_transaction = Transaction(**transaction_data_dict)

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


def create_transactions_batch(
    db: Session, transactions: List[TransactionCreate]
) -> None:
    transactions_dicts = [tx.model_dump(exclude_unset=True) for tx in transactions]
    new_transactions = [Transaction(**t_dict) for t_dict in transactions_dicts]

    # Batch add
    db.add_all(new_transactions)
    db.commit()


async def get_transactions_by_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    currency: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount_out: Optional[int] = None,
    max_amount_out: Optional[int] = None,
    skip: int = 0,
    limit: Optional[int] = 10,
):
    stmt = select(Transaction).where(Transaction.user_id == user_id)

    # Date range filter
    if start_date and end_date:
        stmt = stmt.where(Transaction.date.between(start_date, end_date))
    elif start_date:
        stmt = stmt.where(Transaction.date >= start_date)
    elif end_date:
        stmt = stmt.where(Transaction.date <= end_date)

    # Amount range filter
    if min_amount_out is not None:
        stmt = stmt.where(Transaction.amount >= min_amount_out)
    if max_amount_out is not None:
        stmt = stmt.where(Transaction.amount <= max_amount_out)

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Default sort: date desc, id desc
    stmt = stmt.order_by(Transaction.date.desc(), Transaction.id.desc())

    # Limit
    if limit is not None:
        stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return items, total


async def get_transaction_by_id(
    db: AsyncSession, transaction_id: int
) -> Optional[Transaction]:
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    return result.scalar_one_or_none()


async def update_transaction(
    db: AsyncSession, db_obj: Transaction, obj_in: TransactionUpdate
) -> Transaction:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
