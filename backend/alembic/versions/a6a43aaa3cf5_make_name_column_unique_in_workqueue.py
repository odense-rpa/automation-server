"""make name column unique in workqueue

Revision ID: a6a43aaa3cf5
Revises: 381e4f9d0ff7
Create Date: 2024-12-16 11:08:35.314529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel     


# revision identifiers, used by Alembic.
revision: str = 'a6a43aaa3cf5'
down_revision: Union[str, None] = '381e4f9d0ff7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('workqueue', schema=None) as batch_op:
        batch_op.create_unique_constraint('workqueue_name_constraint', ['name'])



def downgrade() -> None:
    with op.batch_alter_table('workqueue', schema=None) as batch_op:
        batch_op.drop_constraint('workqueue_name_constraint', type_='unique')

