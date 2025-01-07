"""add commandline parameter

Revision ID: 87a8aa53b776
Revises: a6a43aaa3cf5
Create Date: 2025-01-07 12:43:15.016096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel     


# revision identifiers, used by Alembic.
revision: str = '87a8aa53b776'
down_revision: Union[str, None] = 'a6a43aaa3cf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('trigger', sa.Column('parameters', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('trigger', 'parameters')
