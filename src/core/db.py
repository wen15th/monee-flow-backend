# src/core/db.py
from src.core import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import AsyncGenerator


# DB conf
DATABASE_URL = (
    f"postgresql://{config.POSTGRES_USER}:"
    f"{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:"
    f"{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
)
DATABASE_URL_ASYNC = (
    f"postgresql+asyncpg://{config.POSTGRES_USER}:"
    f"{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:"
    f"{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
)

"""Create sync engine"""
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""Create async engine"""
async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
