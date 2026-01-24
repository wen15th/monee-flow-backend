from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.system_category import SystemCategoryRead
from src.schemas.user_category import UserCategoryRead
from src.crud import (
    system_category_crud,
    user_category_crud,
    user_sys_category_prefs_crud,
)


MAX_SYS_CAT_ID = 10000


class CategoryService:
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id

    async def get_user_available_categories(self, db: AsyncSession):
        """
        Get available categories for a user:
        - system categories (exclude disabled)
        - user custom categories (not deleted)
        """
        # Get all system categories
        system_categories = await system_category_crud.list_system_categories(db)

        # Get user disabled system category IDs
        user_prefs = await user_sys_category_prefs_crud.list_user_sys_category_prefs(
            db, self.user_id
        )
        disabled_sys_ids = {
            item.category_id for item in user_prefs if not item.is_enabled
        }

        # Filter out disabled system categories
        enabled_sys_categories = [
            SystemCategoryRead.model_validate(cat)
            for cat in system_categories
            if cat.id not in disabled_sys_ids
        ]

        # Get user custom categories (not deleted)
        user_categories = await user_category_crud.list_user_categories(
            db, self.user_id
        )
        enabled_user_categories = [
            UserCategoryRead.model_validate(cat)
            for cat in user_categories
            if not cat.is_del
        ]

        all_categories = enabled_sys_categories + enabled_user_categories
        return all_categories

    async def check_user_category(self, db: AsyncSession, category_id: int) -> bool:
        # Check system_categories
        if category_id <= MAX_SYS_CAT_ID:
            sys_cat = await system_category_crud.get_system_category_by_id(
                db, category_id
            )
            if not sys_cat:
                raise HTTPException(
                    status_code=400, detail=f"Category {category_id} does not exist"
                )
            user_sys_pref = (
                await user_sys_category_prefs_crud.get_user_sys_category_pref(
                    db, user_id=self.user_id, category_id=category_id
                )
            )
            if user_sys_pref and user_sys_pref.is_enabled == False:
                raise HTTPException(
                    status_code=400, detail=f"Category {category_id} is not enabled"
                )

        # Check user_categories
        else:
            user_cat = await user_category_crud.get_user_category(db, category_id)
            if not user_cat or user_cat.is_del:
                raise HTTPException(
                    status_code=400, detail=f"Category {category_id} does not exist"
                )

        return True

    @staticmethod
    async def get_category_id_name_map(
        db: AsyncSession,
        category_ids: list[int],
    ) -> dict[int, str]:
        if not category_ids:
            return {}

        sys_cats = await system_category_crud.get_system_category_by_ids(
            db=db, category_ids=category_ids
        )
        return {cat.id: cat.name for cat in sys_cats}
