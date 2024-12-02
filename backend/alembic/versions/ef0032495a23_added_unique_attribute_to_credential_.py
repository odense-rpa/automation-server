"""Added unique attribute to Credential name

Revision ID: ef0032495a23
Revises: c0f22b1d3fa0
Create Date: 2024-12-02 14:18:19.244096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel     


# revision identifiers, used by Alembic.
revision: str = 'ef0032495a23'
down_revision: Union[str, None] = 'c0f22b1d3fa0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     with op.batch_alter_table('credential', schema=None) as batch_op:
        batch_op.create_unique_constraint('credential_name_constraint', ['name'])    

def downgrade() -> None:
    with op.batch_alter_table('credential', schema=None) as batch_op:
        batch_op.drop_constraint('credential_name_constraint', type_='unique')