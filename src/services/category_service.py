from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.system_category import SystemCategoryRead
from src.schemas.user_category import UserCategoryRead
from src.crud.system_category_crud import list_system_categories
from src.crud.user_category_crud import list_user_categories
from src.crud.user_sys_category_prefs_crud import list_user_sys_category_prefs


class CategoryService:
    def __init__(self, user_id: str):
        self.user_id = user_id

    async def get_user_available_categories(self, db: AsyncSession):
        """
        Get available categories for a user:
        - system categories (exclude disabled)
        - user custom categories (not deleted)
        """
        # Get all system categories
        system_categories = await list_system_categories(db)

        # Get user disabled system category IDs
        user_prefs = await list_user_sys_category_prefs(db, self.user_id)
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
        user_categories = await list_user_categories(db, self.user_id)
        enabled_user_categories = [
            UserCategoryRead.model_validate(cat)
            for cat in user_categories
            if not cat.is_del
        ]

        all_categories = enabled_sys_categories + enabled_user_categories
        return all_categories
