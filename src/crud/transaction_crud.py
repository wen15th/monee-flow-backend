from sqlalchemy.orm import Session
from typing import Optional, List
from ..models import Transaction
from ..schemas.transaction import TransactionCreate
import uuid

def create_transaction(db: Session, transaction_data: TransactionCreate) -> Transaction:
    transaction_data_dict = transaction_data.model_dump(exclude_unset=True)
    new_transaction = Transaction(**transaction_data_dict)

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


def get_transactions_by_user(
        db: Session,
        user_id: uuid.UUID,
        status: Optional[int] = 1,
        skip: int = 0,
        limit: Optional[int] = 10
) -> List[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if status is not None:
        query = query.filter(Transaction.status == status)

    if limit is not None:
        query = query.offset(skip).limit(limit)

    return query.all()


def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).one_or_none()
