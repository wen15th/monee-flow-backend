from src.crud.statement_crud import create_statement, get_statement_by_id, get_statements_by_user
from src.schemas.statement import StatementCreate
from src.models import Statement
from datetime import datetime
from uuid import UUID


def test_create_statement(db_session):
    """
    Test whether create_statement can insert data correctly
    """
    statement_data = StatementCreate(
        user_id="804659e9-6351-4723-b829-19a20f210bc6",
        s3_key="path/to/statement.csv",
        source="Test",
        # Convert str to datetime
        start_time=datetime.fromisoformat("2025-07-01 00:00:00"),
        end_time=datetime.fromisoformat("2025-07-31 23:59:59"),
    )

    new_statement = create_statement(db_session, statement_data)

    # Get inserted data and compare
    inserted_statement = get_statement_by_id(db_session, new_statement.id)

    assert inserted_statement.user_id == statement_data.user_id
    assert inserted_statement.s3_key == statement_data.s3_key
    assert inserted_statement.source == statement_data.source
    assert inserted_statement.start_time == statement_data.start_time
    assert inserted_statement.end_time == statement_data.end_time


def test_get_statements_by_user(db_session):
    user_id = UUID("804659e9-6351-4723-b829-19a20f210bc6")
    statements = get_statements_by_user(db_session, user_id)

    assert isinstance(statements, list)
    for s in statements:
        assert isinstance(s, Statement)
        assert s.user_id == user_id
        assert s.source == 'Test'
        assert s.start_time == datetime.fromisoformat('2025-07-01 00:00:00')
        assert s.end_time == datetime.fromisoformat('2025-07-01 23:59:59')