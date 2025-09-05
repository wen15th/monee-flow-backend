from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.system_category import SystemCategory
from src.schemas.system_category import SystemCategoryCreate


async def create_system_category(db: AsyncSession, obj_in: SystemCategoryCreate):
    db_obj = SystemCategory(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_system_category(db: AsyncSession, category_id: int):
    result = await db.execute(
        select(SystemCategory).where(SystemCategory.id == category_id)
    )
    return result.scalar_one_or_none()


async def list_system_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(SystemCategory).offset(skip).limit(limit))
    return result.scalars().all()


async def update_system_category(db: AsyncSession, category_id: int, values: dict):
    await db.execute(
        update(SystemCategory).where(SystemCategory.id == category_id).values(**values)
    )
    await db.commit()
    return await get_system_category(db, category_id)
