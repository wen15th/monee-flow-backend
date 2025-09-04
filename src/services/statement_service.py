# services/statement_service.py
import logging
from pathlib import Path
from fastapi import UploadFile
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.enums import BankEnum
from src.schemas.statement import StatementCreate
from src.crud.statement_crud import create_statement
import os
import uuid


class StatementService:
    def __init__(self, tmp_dir: str = None):
        self.tmp_dir = Path(tmp_dir or os.getenv("TMP_DATA_PATH", "./tmp_data"))
        self.tmp_dir.mkdir(parents=True, exist_ok=True)


    def get_user_dir(self, user_id: uuid.UUID) -> Path:
        """Get user dir and make sure it exists"""
        user_dir = self.tmp_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir


    def generate_filename(self, original_name: str, bank: BankEnum) -> str:
        """Generate file name：bank_YYYYMMDD_HHMMSS.csv"""
        name, ext = os.path.splitext(original_name.strip())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{bank.value}_{timestamp}{ext}"


    async def save_statement_file(
        self, file: UploadFile, bank: BankEnum, user_id: uuid.UUID
    ) -> str:
        """Save file to user dir"""
        user_dir = self.get_user_dir(user_id)
        new_filename = self.generate_filename(file.filename, bank)
        save_path = user_dir / new_filename

        # Save file asynchronously
        content = await file.read()
        save_path.write_bytes(content)

        return str(save_path)


    async def create_statement_record(
            self,
            db: AsyncSession,
            user_id: uuid.UUID,
            bank: BankEnum,
            file_path: str
    ):
        stmt_data = StatementCreate(
            user_id=user_id,
            s3_key=file_path,
            # TODO: parse real start and end time
            start_time=datetime(1970, 1, 1),
            end_time=datetime(1970, 1, 1),
            source=bank.value,
        )
        try:
            stmt_id = await create_statement(db, stmt_data)
            return stmt_id
        except Exception as e:
            logging.error(f"DB error: {e}")
