import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
import uuid


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


@pytest.fixture(scope="session")
def test_user_id():
    return uuid.UUID("804659e9-6351-4723-b829-19a20f210bc6")