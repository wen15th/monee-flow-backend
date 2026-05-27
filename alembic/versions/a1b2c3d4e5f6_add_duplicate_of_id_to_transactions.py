"""add duplicate_of_id to transactions

Revision ID: a1b2c3d4e5f6
Revises: 7b20758b6540
Create Date: 2026-05-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7b20758b6540'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('transactions', sa.Column('duplicate_of_id', sa.BigInteger(), nullable=True))
    op.drop_constraint('chk_status_valid', 'transactions', type_='check')
    op.create_check_constraint('chk_status_valid', 'transactions', 'status IN (1,2,3)')


def downgrade() -> None:
    op.drop_column('transactions', 'duplicate_of_id')
    op.drop_constraint('chk_status_valid', 'transactions', type_='check')
    op.create_check_constraint('chk_status_valid', 'transactions', 'status IN (1,2)')
