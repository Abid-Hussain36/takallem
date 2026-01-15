"""Update module unique constraint to include dialect

Revision ID: g8h9i0j1k2l3
Revises: 66e0651fbc6e
Create Date: 2026-01-15 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g8h9i0j1k2l3'
down_revision: Union[str, None] = '66e0651fbc6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old unique constraint
    op.drop_constraint('uq_course_unit_section_number', 'modules', type_='unique')
    
    # Create new unique constraint with dialect
    op.create_unique_constraint('uq_course_unit_section_number', 'modules', 
        ['course', 'unit', 'section', 'number', 'dialect'])


def downgrade() -> None:
    # Drop the new constraint
    op.drop_constraint('uq_course_unit_section_number', 'modules', type_='unique')
    
    # Recreate the old constraint without dialect
    op.create_unique_constraint('uq_course_unit_section_number', 'modules', 
        ['course', 'unit', 'section', 'number'])
