import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base
from dotenv import load_dotenv
import os


load_dotenv()
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create db engine
engine = create_engine(DATABASE_URL)

# Create session local factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Configure db session
    """
    # Create db connection
    connection = engine.connect()
    # Start transaction
    transaction = connection.begin()
    # Bind connection to session
    db = TestingSessionLocal(bind=connection)

    try:
        yield db
    finally:
        # Rollback all test changes
        transaction.rollback()
        connection.close()
