"""add incident table

Revision ID: 0dc924f3af5c
Revises: b3f1a2c4d5e6
Create Date: 2026-02-18 10:04:43.192094

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0dc924f3af5c"
down_revision: Union[str, None] = "b3f1a2c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incident",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("NEW", "DISMISSED", "RESCHEDULED", name="incidentstatus"),
            nullable=False,
        ),
        sa.Column(
            "error_trace", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("resolution_note", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "ai_resolution_suggestion",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column("rescheduled_session_id", sa.Integer(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["process_id"], ["process.id"]),
        sa.ForeignKeyConstraint(["rescheduled_session_id"], ["session.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["session.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_incident_session_id", "incident", ["session_id"])
    op.create_index("ix_incident_status", "incident", ["status"])


def downgrade() -> None:
    op.drop_index("ix_incident_status", table_name="incident")
    op.drop_index("ix_incident_session_id", table_name="incident")
    op.drop_table("incident")
    op.execute("DROP TYPE IF EXISTS incidentstatus")
