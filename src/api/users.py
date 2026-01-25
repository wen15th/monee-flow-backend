import logging

from fastapi import APIRouter, Depends, Response, Cookie, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.schemas.user import AuthUser
from src.services.user_service import UserService
from src.schemas.user import UserCreate, UserRead, Token
from src.core.db import get_async_session
from typing import Optional


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
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by deleting refresh_token cookie.
    """
    response.delete_cookie(
        key="refresh_token", httponly=True, secure=True, samesite="lax"
    )
    return {"message": "Logged out successfully"}


@router.post("/token/refresh", response_model=Token)
async def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token"),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    try:
        # Verify refresh token
        user_id = UserService.verify_refresh_token(refresh_token)

        # Generate new access tokens
        access_token = UserService.create_access_token(user_id)
        new_refresh_token = UserService.create_refresh_token(user_id)

        # Set new refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 7,  # 7 days
        )

        return Token(access_token=access_token)
    except Exception as e:
        logging.error(f"[AuthUser] Refresh token failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/me", response_model=UserRead)
async def get_me(
    db: AsyncSession = Depends(get_async_session),
    user: AuthUser = Depends(get_current_user),
):
    return await UserService(user.user_id).get_user_by_id(db=db)
