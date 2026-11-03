"""add datastore table

Revision ID: 5d2a9e7c1b40
Revises: 9c4c8c4d4e9f
Create Date: 2026-11-03 12:00:00.000000

Datastores are named JSON documents that automations keep state in between
runs. `data` is TEXT, not JSONB: it holds the JSON encrypted at rest (enc:v1:)
when an encryption key is configured. Names are unique among datastores that
aren't deleted (partial unique index), so a deleted name can be reused.

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5d2a9e7c1b40"
down_revision: Union[str, None] = "9c4c8c4d4e9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "datastore",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_datastore_name_active",
        "datastore",
        ["name"],
        unique=True,
        postgresql_where=sa.text("NOT deleted"),
    )


def downgrade() -> None:
    op.drop_index("uq_datastore_name_active", table_name="datastore")
    op.drop_table("datastore")
