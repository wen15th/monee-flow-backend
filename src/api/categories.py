from src.core.db import get_async_session
from src.services.category_service import CategoryService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter


router = APIRouter(prefix="/user/categories", tags=["categories"])


@router.get("")
async def get_user_categories(
    user_id: str, db: AsyncSession = Depends(get_async_session)
):
    service = CategoryService(user_id)
    categories = await service.get_user_available_categories(db)
    return categories
