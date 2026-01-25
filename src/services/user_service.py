from fastapi import HTTPException
from pydantic import EmailStr
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from src.crud import user_crud
from src.schemas.user import UserCreate, UserRead
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from src.core import config
from jwt import PyJWTError
import jwt

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id

    @staticmethod
    async def register(db: AsyncSession, user_in: UserCreate) -> UserRead:
        # 1. Check if email already exists
        existing_user = await user_crud.get_user_by_email(db, str(user_in.email))
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 2. Hash pwd
        hashed_pw = pwd_context.hash(user_in.password)

        # 3. Save to db
        new_user = await user_crud.create_user(
            db, user_in.first_name, user_in.last_name, str(user_in.email), hashed_pw
        )

        return UserRead.model_validate(new_user)

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: EmailStr, password: str):
        user = await user_crud.get_user_by_email(db, email=str(email))
        if (not user) or (not pwd_context.verify(password, user.password_hash)):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        return user

    @staticmethod
    def create_access_token(user_id: str) -> str:
        expire = datetime.now() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": user_id, "exp": expire}
        return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        expire = datetime.now() + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {"sub": user_id, "exp": expire}
        return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

    @staticmethod
    def verify_refresh_token(token: str) -> str:
        try:
            payload = jwt.decode(
                token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            return user_id
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    async def get_user_by_id(self, db: AsyncSession) -> UserRead:
        user = await user_crud.get_user_by_id(db=db, user_id=self.user_id)
        return UserRead.model_validate(user)
