"""Add VOCAB_LISTENING_PROBLEM_SETS enum value to resourcetype

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-01-10 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add VOCAB_LISTENING_PROBLEM_SETS to the resourcetype enum
    op.execute("ALTER TYPE resourcetype ADD VALUE 'VOCAB_LISTENING_PROBLEM_SETS'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values directly.
    pass

