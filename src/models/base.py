# src/models/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.db import DATABASE_URL


# Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL, echo=True)

# Create Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM Base
Base = declarative_base()