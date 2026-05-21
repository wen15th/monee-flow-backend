from src.core.auth import get_current_user
from src.schemas.user import AuthUser
from src.core.db import get_async_session
from src.services.category_service import CategoryService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter
import uuid


router = APIRouter(
    prefix="/user/categories",
    tags=["categories"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
async def get_user_categories(
    db: AsyncSession = Depends(get_async_session),
    user: AuthUser = Depends(get_current_user),
):
    service = CategoryService(uuid.UUID(user.user_id))
    categories = await service.get_user_available_categories(db=db)
    return categories
