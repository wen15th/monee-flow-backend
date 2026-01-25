from src.core.auth import get_current_user
from src.services.parsers.factory import get_parser
from src.services.statement_service import StatementService
from src.schemas.enums import BankEnum
from src.schemas.user import AuthUser
from src.schemas.common import PaginatedResponse
from src.schemas.statement import StatementRead
from fastapi import (
    Depends,
    BackgroundTasks,
    UploadFile,
    File,
    Form,
    HTTPException,
    APIRouter,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_async_session
import uuid

router = APIRouter(
    prefix="/statements", tags=["statements"], dependencies=[Depends(get_current_user)]
)


@router.post("")
async def upload_statement(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    bank: BankEnum = Form(...),
    currency: str = Form(...),
    db: AsyncSession = Depends(get_async_session),
    user: AuthUser = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed.")

    user_id = uuid.UUID(user.user_id)

    # Save file
    statement_service = StatementService()
    file_path = await statement_service.save_statement_file(file, bank, user_id)

    # Save statement record to db
    stmt_id = await statement_service.create_statement_record(
        db=db, user_id=user_id, bank=bank, currency=currency, file_path=file_path
    )

    # Run parser asynchronously after file upload
    parser = get_parser(bank.value)
    background_tasks.add_task(
        parser.parse,
        user_id=user_id,
        stmt_id=stmt_id,
        currency=currency,
        file_path=file_path,
    )

    return {"message": "Upload successful", "file_path": file_path}


# api
@router.get("", response_model=PaginatedResponse[StatementRead])
async def get_statements(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_async_session),
    user: AuthUser = Depends(get_current_user),
):
    return await StatementService.get_user_statements(
        db, uuid.UUID(user.user_id), page=page, page_size=page_size
    )
