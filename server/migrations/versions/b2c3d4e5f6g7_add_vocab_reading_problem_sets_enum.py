"""Add VOCAB_READING_PROBLEM_SETS enum value to resourcetype

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-10 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add VOCAB_READING_PROBLEM_SETS to the resourcetype enum
    op.execute("ALTER TYPE resourcetype ADD VALUE 'VOCAB_READING_PROBLEM_SETS'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values directly.
    pass

