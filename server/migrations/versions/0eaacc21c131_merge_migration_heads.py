"""Merge migration heads

Revision ID: 0eaacc21c131
Revises: 221d4bc6fd0f, d4e5f6g7h8i9
Create Date: 2026-01-10 21:39:58.818678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0eaacc21c131'
down_revision: Union[str, None] = ('221d4bc6fd0f', 'd4e5f6g7h8i9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
