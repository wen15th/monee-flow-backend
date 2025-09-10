from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user import User
from typing import Optional


async def create_user(
    db: AsyncSession, first_name: str, last_name: str, email: str, pwd_hash: str
) -> User:
    db_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=pwd_hash,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(
    db: AsyncSession, email: str, is_active: Optional[bool] = True
) -> Optional[User]:
    stmt = select(User).where(User.email == email)

    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)

    result = await db.execute(stmt)
    return result.scalars().first()
