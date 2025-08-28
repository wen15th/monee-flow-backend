from src.crud.statement_crud import create_statement
from src.schemas.statement import StatementCreate
from datetime import datetime

def test_create_statement(db_session):
    """
    Test whether create_statement can insert data correctly
    """
    statement_data = StatementCreate(
        user_id="123e4567-e89b-12d3-a456-426614174000",
        s3_key="path/to/statement.csv",
        source="Test",
        # Convert str to datetime
        start_time=datetime.fromisoformat("2025-07-01T00:00:00"),
        end_time=datetime.fromisoformat("2025-07-31T23:59:59"),
    )

    new_statement = create_statement(db_session, statement_data)

    print(new_statement)