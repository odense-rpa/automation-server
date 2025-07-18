"""Add work duration tracking fields to WorkItem

Revision ID: 9359bc77847e
Revises: 709b9d181fe8
Create Date: 2025-07-18 10:10:44.039527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel     


# revision identifiers, used by Alembic.
revision: str = '9359bc77847e'
down_revision: Union[str, None] = '709b9d181fe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add started_at and work_duration_seconds columns to workitem table
    op.add_column('workitem', sa.Column('started_at', sa.DateTime(), nullable=True))
    op.add_column('workitem', sa.Column('work_duration_seconds', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('workitem', 'work_duration_seconds')
    op.drop_column('workitem', 'started_at')
