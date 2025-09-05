from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional, List
from src.models import Transaction
from src.schemas.transaction import TransactionCreate
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
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
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


def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).one_or_none()
