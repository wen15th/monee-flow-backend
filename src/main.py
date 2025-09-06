import logging

from src.services.transaction_service import TransactionService
from src.schemas.transaction import TransactionRead, TransactionUpdate
from src.services.parsers.factory import get_parser
from src.services.statement_service import StatementService
from src.services.category_service import CategoryService
from src.schemas.enums import BankEnum
from src.schemas.common import PaginatedResponse
from src.schemas.statement import StatementRead
from fastapi import (
    FastAPI,
    Depends,
    BackgroundTasks,
    UploadFile,
    File,
    Form,
    HTTPException,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_async_session
from typing import Optional
from datetime import date
import uuid

# Log conf
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Monee Flow Backend is running 😁"}


@app.post("/statement")
async def upload_statement(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: uuid.UUID = Form(...),
    bank: BankEnum = Form(...),
    db: AsyncSession = Depends(get_async_session),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed.")

    # Save file
    statement_service = StatementService()
    file_path = await statement_service.save_statement_file(file, bank, user_id)

    # Save statement record to db
    stmt_id = await statement_service.create_statement_record(
        db, user_id, bank, file_path
    )

    # Run parser asynchronously after file upload
    parser = get_parser(bank.value)
    background_tasks.add_task(
        parser.parse, user_id=user_id, stmt_id=stmt_id, file_path=file_path
    )

    return {"message": "Upload successful", "file_path": file_path}


# api
@app.get("/statements", response_model=PaginatedResponse[StatementRead])
async def get_statements(
    user_id: uuid.UUID,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_async_session),
):
    return await StatementService.get_user_statements(
        db, user_id, page=page, page_size=page_size
    )


@app.get("/transactions", response_model=PaginatedResponse[TransactionRead])
async def get_transactions(
    user_id: uuid.UUID,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
):
    return await TransactionService.get_user_transactions(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@app.patch("/transaction/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: int,
    user_id: uuid.UUID,
    tx_update: TransactionUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    return await TransactionService.update_transaction(
        db=db, transaction_id=transaction_id, user_id=user_id, tx_update=tx_update
    )


@app.get("/user_categories")
async def get_user_categories(
    user_id: str, db: AsyncSession = Depends(get_async_session)
):
    service = CategoryService(user_id)
    categories = await service.get_user_available_categories(db)
    return categories
