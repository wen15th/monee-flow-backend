# services/statement_service.py
import logging
import asyncio
from pathlib import Path
from fastapi import UploadFile
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.common import PaginatedResponse
from src.schemas.enums import BankEnum
from src.schemas.statement import StatementCreate, StatementRead, StatementDeleteResult
from src.crud import transaction_crud, statement_crud
import os
import uuid


class StatementService:

    class NotFoundOrNoAccess(Exception):
        pass

    class Conflict(Exception):
        pass

    STATUS_ACTIVE = 1
    STATUS_DELETED = 2

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

    @staticmethod
    async def create_statement_record(
        db: AsyncSession,
        user_id: uuid.UUID,
        bank: BankEnum,
        currency: str,
        file_path: str,
    ):
        stmt_data = StatementCreate(
            user_id=user_id,
            s3_key=file_path,
            # TODO: parse real start and end time
            start_time=datetime(1970, 1, 1),
            end_time=datetime(1970, 1, 1),
            source=bank.value,
            currency=currency,
        )
        try:
            stmt_id = await statement_crud.create_statement(db, stmt_data)
            return stmt_id
        except Exception as e:
            logging.error(f"DB error: {e}")

    @staticmethod
    async def get_user_statements(
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
        status: Optional[int] = 1,
    ) -> PaginatedResponse[StatementRead]:
        skip = (page - 1) * page_size

        statements, total = await statement_crud.get_statements_by_user(
            db, user_id, status=status, skip=skip, limit=page_size
        )
        return PaginatedResponse[StatementRead](
            items=[StatementRead.model_validate(stmt) for stmt in statements],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def delete_statement(
        self,
        *,
        db: AsyncSession,
        user_id,
        statement_id,
        delete_transactions: bool,
    ) -> StatementDeleteResult:
        """
        Soft-delete statement (status=2) and optionally its transactions (status=2),
        then delete file from filesystem.

        DB changes are committed first; file deletion is best-effort (log on failure).
        """

        # 1) Fetch statement (owner scoped) to get file_path + current status
        stmt = await statement_crud.get_statement_by_id(
            db=db,
            statement_id=statement_id,
        )
        if stmt is None or stmt.user_id != user_id:
            raise self.NotFoundOrNoAccess()

        # TODO: if statement is under processing, it cannot be deleted
        # if stmt.status == SOME_PROCESSING_STATUS:
        #     raise self.Conflict()

        file_path = getattr(stmt, "s3_key", None)
        current_status = getattr(stmt, "status", None)

        # 2) If already deleted => idempotent success
        if current_status == self.STATUS_DELETED:
            return

        # 3) Soft-delete in DB within a transaction
        try:
            # 3.1 update statement status
            updated = await statement_crud.soft_delete_by_id(
                db=db,
                statement_id=statement_id,
                deleted_status=self.STATUS_DELETED,
            )
            if updated == 0:
                raise self.NotFoundOrNoAccess()

            # 3.2 soft-delete related transactions
            tx_affected = 0
            if delete_transactions:
                tx_affected = await transaction_crud.soft_delete_by_statement_id(
                    db=db,
                    statement_id=statement_id,
                    deleted_status=self.STATUS_DELETED,
                )

            await db.commit()

            logging.info(
                "[delete_statement] Succeeded: user_id=%s statement_id=%s delete_transactions=%s tx_affected=%s",
                str(user_id),
                str(statement_id),
                delete_transactions,
                tx_affected,
            )
        except Exception:
            await db.rollback()
            logging.exception(
                "[delete_statement] Failed: user_id=%s statement_id=%s delete_transactions=%s",
                str(user_id),
                str(statement_id),
                delete_transactions,
            )
            raise

        # 4) Delete file after DB commit (best effort)
        file_deleted, file_delete_err = await self._delete_file(
            file_path=file_path, statement_id=statement_id
        )

        return StatementDeleteResult(
            statement_id=statement_id,
            deleted=True,
            transactions_affected=tx_affected,
            file_deleted=file_deleted,
            file_delete_error=file_delete_err,
        )

    async def _delete_file(
        self, file_path: Optional[str], statement_id
    ) -> tuple[bool, Optional[str]]:
        if not file_path:
            # Consider this case as success
            return True, None

        try:
            await asyncio.to_thread(self._remove_file_if_exists, file_path)
            return True, None
        except Exception as e:
            logging.exception(
                "statement_file_delete_failed statement_id=%s file_path=%s",
                str(statement_id),
                file_path,
            )
            return False, str(e)

    @staticmethod
    def _remove_file_if_exists(file_path: str) -> None:
        try:
            os.remove(file_path)
            logging.info(f"[remove file] Successful. File: {file_path} deleted")
        except FileNotFoundError:
            return
