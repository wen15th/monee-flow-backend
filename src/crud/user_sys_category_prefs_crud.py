from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user_sys_category_pref import UserSysCategoryRead
from src.models.user_sys_category_pref import UserSysCategoryPref


async def create_user_sys_category_pref(
    db: AsyncSession, user_id: str, category_id: int, is_enabled: bool = True
):
    db_obj = UserSysCategoryPref(
        user_id=user_id, category_id=category_id, is_enabled=is_enabled
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_user_sys_category_pref(
    db: AsyncSession, user_id: str, category_id: int
) -> Optional[UserSysCategoryPref]:
    result = await db.execute(
        select(UserSysCategoryPref)
        .where(UserSysCategoryPref.user_id == user_id)
        .where(UserSysCategoryPref.category_id == category_id)
    )
    return result.scalar_one_or_none()


async def list_user_sys_category_prefs(db: AsyncSession, user_id: str):
    result = await db.execute(
        select(UserSysCategoryPref).where(UserSysCategoryPref.user_id == user_id)
    )
    return result.scalars().all()


async def update_user_sys_category_pref(
    db: AsyncSession, user_id: str, category_id: int, is_enabled: bool
):
    obj = await get_user_sys_category_pref(db, user_id, category_id)
    if obj:
        obj.is_enabled = is_enabled
        await db.commit()
        await db.refresh(obj)
    return obj
