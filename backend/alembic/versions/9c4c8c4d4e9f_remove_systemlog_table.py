"""remove systemlog table

Revision ID: 9c4c8c4d4e9f
Revises: e7c1f0a2b9d4
Create Date: 2026-07-27 13:18:54.544205

The systemlog table was created by the initial migration but never used:
the SystemLog model had no repository, service or router, and nothing ever
wrote a row. Removed along with the model.

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9c4c8c4d4e9f"
down_revision: Union[str, None] = "e7c1f0a2b9d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("systemlog")


def downgrade() -> None:
    # Mirrors the definition from c0f22b1d3fa0_initial_autogeneration.py
    op.create_table(
        "systemlog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("level", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
