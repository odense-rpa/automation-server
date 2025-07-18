"""Added data text field to credentials

Revision ID: 381e4f9d0ff7
Revises: ef0032495a23
Create Date: 2024-12-04 10:14:04.623886

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "381e4f9d0ff7"
down_revision: Union[str, None] = "ef0032495a23"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    context = op.get_context()
    dialect_name = context.dialect.name

    if dialect_name == "postgresql":
        target_json_type = postgresql.JSONB(astext_type=sa.Text())
    else:
        target_json_type = sa.Text()

    op.add_column("credential", sa.Column("data", target_json_type, nullable=True))


def downgrade() -> None:
    op.drop_column("credential", "data")
