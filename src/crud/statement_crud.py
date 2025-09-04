from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from ..models import Statement
from ..schemas.statement import StatementCreate
import uuid


async def create_statement(db: AsyncSession, statement_data: StatementCreate):
    stmt = Statement(**statement_data.model_dump())
    db.add(stmt)
    await db.commit()
    await db.refresh(stmt)
    return stmt.id


async def get_statements_by_user(
        db: AsyncSession,
        user_id: uuid.UUID,
        status: Optional[int] = 1,
        skip: int = 0,
        limit: Optional[int] = 10
) -> List[Statement]:
    stmt = select(Statement).where(Statement.user_id == user_id)

    if status is not None:
        stmt = stmt.where(Statement.status == status)

    if limit is not None:
        stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_statement_by_id(
    db: AsyncSession, statement_id: int
) -> Optional[Statement]:
    stmt = select(Statement).where(Statement.id == statement_id)
    result = await db.execute(stmt)
    return result.scalars().first()
