"""Add git_options column to process

Revision ID: d41f7c9e2b10
Revises: 0dc924f3af5c
Create Date: 2026-07-08 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d41f7c9e2b10"
down_revision: Union[str, None] = "0dc924f3af5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "process",
        sa.Column("git_options", sa.String(), nullable=True, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("process", "git_options")
