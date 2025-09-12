import logging

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserRead, Token
from src.core.db import get_async_session

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    return await UserService.register(db, user)


@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    email = form_data.username
    user = await UserService.authenticate_user(db, email, form_data.password)
    access_token = UserService.create_access_token(str(user.id))
    refresh_token = UserService.create_refresh_token(str(user.id))
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Only via HTTPS
        samesite="none",
        max_age=60 * 60,  # 1 hour
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return {"message": "Successful"}


@router.post("/token/refresh", response_model=Token)
async def refresh(refresh_token: str):
    user_id = UserService.verify_refresh_token(refresh_token)
    access_token = UserService.create_access_token(user_id)
    new_refresh_token = UserService.create_refresh_token(user_id)
    return Token(access_token=access_token, refresh_token=new_refresh_token)
