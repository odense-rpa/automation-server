"""add commandline parameter to session

Revision ID: 709b9d181fe8
Revises: 87a8aa53b776
Create Date: 2025-01-07 13:17:34.631369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel     


# revision identifiers, used by Alembic.
revision: str = '709b9d181fe8'
down_revision: Union[str, None] = '87a8aa53b776'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.add_column('session', sa.Column('parameters', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('session', 'parameters')
