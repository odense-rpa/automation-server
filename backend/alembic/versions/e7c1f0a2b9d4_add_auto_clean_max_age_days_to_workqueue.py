"""Add auto_clean_max_age_days to workqueue

Revision ID: e7c1f0a2b9d4
Revises: d41f7c9e2b10
Create Date: 2026-07-08 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7c1f0a2b9d4"
down_revision: Union[str, None] = "d41f7c9e2b10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "workqueue",
        sa.Column("auto_clean_max_age_days", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("workqueue", "auto_clean_max_age_days")
