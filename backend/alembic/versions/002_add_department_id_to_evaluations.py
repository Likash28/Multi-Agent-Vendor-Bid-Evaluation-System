"""Add department_id to evaluations

Revision ID: 002
Revises: 001
Create Date: 2024-12-20 19:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add department_id column to evaluations table
    op.add_column(
        'evaluations',
        sa.Column('department_id', sa.String(36), sa.ForeignKey('departments.id'), nullable=True)
    )
    op.create_index('ix_evaluations_department_id', 'evaluations', ['department_id'])


def downgrade() -> None:
    op.drop_index('ix_evaluations_department_id', table_name='evaluations')
    op.drop_column('evaluations', 'department_id')

