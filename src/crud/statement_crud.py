from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
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
    limit: Optional[int] = 10,
):
    stmt = select(Statement).where(Statement.user_id == user_id)
    # Where: status
    if status is not None:
        stmt = stmt.where(Statement.status == status)
    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Default sort: id desc
    stmt = stmt.order_by(Statement.id.desc())
    # Limit
    if limit is not None:
        stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return items, total


async def get_statement_by_id(
    db: AsyncSession, statement_id: int
) -> Optional[Statement]:
    stmt = select(Statement).where(Statement.id == statement_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def soft_delete_by_id(
    *,
    db: AsyncSession,
    statement_id,
    deleted_status: int,
) -> int:
    """
    Return affected row count.
    updated_at：如果你依赖 ORM/onupdate 自动更新，这里也可以不显式 set；
    为了确定性，建议显式写 updated_at=func.now()（见下方可选写法）。
    """
    q = (
        update(Statement)
        .where(Statement.id == statement_id)
        .where(Statement.status != deleted_status)  # idempotent
        .values(status=deleted_status)
    )
    res = await db.execute(q)
    return res.rowcount or 0
