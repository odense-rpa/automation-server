"""Add composite index on workitem(workqueue_id, status)

Revision ID: b3f1a2c4d5e6
Revises: a967e43074d6
Create Date: 2026-02-17 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b3f1a2c4d5e6"
down_revision: Union[str, None] = "a967e43074d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_workitem_workqueue_id_status",
        "workitem",
        ["workqueue_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_workitem_workqueue_id_status", table_name="workitem")
