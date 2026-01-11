"""Add DIALECT_SELECTION enum value to resourcetype

Revision ID: a1b2c3d4e5f6
Revises: 637362d9aadf
Create Date: 2026-01-10 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '637362d9aadf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add DIALECT_SELECTION to the resourcetype enum
    op.execute("ALTER TYPE resourcetype ADD VALUE 'DIALECT_SELECTION'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values directly.
    # DIALECT_SELECTION will remain in resourcetype enum after downgrade.
    pass

