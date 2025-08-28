from sqlalchemy.orm import Session
from typing import Optional, List
from ..models import Statement
from ..schemas.statement import StatementCreate
import uuid

def create_statement(db: Session, statement_data: StatementCreate) -> Statement:
    statement_data_dict = statement_data.model_dump(exclude_unset=True)
    new_statement = Statement(**statement_data_dict)

    db.add(new_statement)
    db.commit()

    # Update the new_statement object with database-generated values
    db.refresh(new_statement)

    return new_statement


def get_statements_by_user(
        db: Session,
        user_id: uuid.UUID,
        status: Optional[int] = 1,
        skip: int = 0,
        limit: Optional[int] = 10
) -> List[Statement]:
    query = db.query(Statement).filter(Statement.user_id == user_id)

    if status is not None:
        query = query.filter(Statement.status == status)

    if limit is not None:
        query = query.offset(skip).limit(limit)

    return query.all()


def get_statement_by_id(db: Session, statement_id: int) -> Optional[Statement]:
    return db.query(Statement).filter(Statement.id == statement_id).one_or_none()
