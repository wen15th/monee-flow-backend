import decimal

from src.schemas.transaction import TransactionCreate
from src.crud.transaction_crud import create_transaction, get_transactions_by_user, get_transaction_by_id
from src.models import Transaction
from datetime import date


def test_create_transaction(db_session, test_user_id):
    """
    Test whether create_statement can insert data correctly
    """
    transaction_data = TransactionCreate(
        user_id=test_user_id,
        statement_id=11,
        transaction_date=date.fromisoformat("2025-07-07"),
        posted_date=date.fromisoformat("2025-07-08"),
        merchant_name="RCSS #1009",
        merchant_category="Grocery Stores and Supermarkets",
        customized_category="",
        # Use str to avoid floating point precision issues (e.g. 136.0399999999).
        amount=decimal.Decimal("136.04")
    )

    new_transaction = create_transaction(db_session, transaction_data)

    # Get inserted data and compare
    inserted_statement = get_transaction_by_id(db_session, new_transaction.id)

    assert inserted_statement.user_id == transaction_data.user_id
    assert inserted_statement.statement_id == transaction_data.statement_id
    assert inserted_statement.transaction_date == transaction_data.transaction_date
    assert inserted_statement.posted_date == transaction_data.posted_date
    assert inserted_statement.merchant_name == transaction_data.merchant_name
    assert inserted_statement.merchant_category == transaction_data.merchant_category
    assert inserted_statement.customized_category == transaction_data.customized_category
    assert inserted_statement.amount == transaction_data.amount


def test_get_statements_by_user(db_session, test_user_id):

    transactions = get_transactions_by_user(db_session, test_user_id)

    assert isinstance(transactions, list)
    for s in transactions:
        assert isinstance(s, Transaction)
        assert s.user_id == test_user_id
        assert s.status == 1