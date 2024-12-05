"""Added data text field to credentials

Revision ID: 381e4f9d0ff7
Revises: ef0032495a23
Create Date: 2024-12-04 10:14:04.623886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel     


# revision identifiers, used by Alembic.
revision: str = '381e4f9d0ff7'
down_revision: Union[str, None] = 'ef0032495a23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('credential', sa.Column('data', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('credential', 'data')