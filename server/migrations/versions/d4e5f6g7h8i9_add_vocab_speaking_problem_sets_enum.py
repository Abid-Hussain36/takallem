"""Add VOCAB_SPEAKING_PROBLEM_SETS enum value to resourcetype

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-01-10 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add VOCAB_SPEAKING_PROBLEM_SETS to the resourcetype enum
    op.execute("ALTER TYPE resourcetype ADD VALUE 'VOCAB_SPEAKING_PROBLEM_SETS'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values directly.
    pass

