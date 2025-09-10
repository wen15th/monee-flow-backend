from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserRead, Token
from src.core.db import get_async_session

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    return await UserService.register(db, user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    email = form_data.username
    user = await UserService.authenticate_user(db, email, form_data.password)
    access_token = UserService.create_access_token(str(user.id))
    refresh_token = UserService.create_refresh_token(str(user.id))

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/token/refresh", response_model=Token)
async def refresh(refresh_token: str):
    user_id = UserService.verify_refresh_token(refresh_token)
    access_token = UserService.create_access_token(user_id)
    new_refresh_token = UserService.create_refresh_token(user_id)
    return Token(access_token=access_token, refresh_token=new_refresh_token)
