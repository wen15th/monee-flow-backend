from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user_category import UserCategory
from src.schemas.user_category import UserCategoryCreate


async def create_user_category(db: AsyncSession, obj_in: UserCategoryCreate):
    db_obj = UserCategory(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_user_category(db: AsyncSession, category_id: int):
    result = await db.execute(
        select(UserCategory).where(UserCategory.id == category_id)
    )
    return result.scalar_one_or_none()


async def list_user_categories(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100
):
    result = await db.execute(
        select(UserCategory)
        .where(UserCategory.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def delete_user_category(db: AsyncSession, category_id: int):
    obj = await get_user_category(db, category_id)
    if obj:
        obj.is_del = True
        await db.commit()
    return obj
