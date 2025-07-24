"""Rename sessionlog table to auditlog

Revision ID: a967e43074d6
Revises: 95f5482ed959
Create Date: 2025-07-23 21:51:16.423892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel     


# revision identifiers, used by Alembic.
revision: str = 'a967e43074d6'
down_revision: Union[str, None] = '95f5482ed959'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the table
    op.rename_table('sessionlog', 'auditlog')
    
    # Update the foreign key constraint names (PostgreSQL specific)
    op.execute('ALTER TABLE auditlog RENAME CONSTRAINT sessionlog_pkey TO auditlog_pkey')
    op.execute('ALTER TABLE auditlog RENAME CONSTRAINT sessionlog_session_id_fkey TO auditlog_session_id_fkey')
    op.execute('ALTER TABLE auditlog RENAME CONSTRAINT sessionlog_workitem_id_fkey TO auditlog_workitem_id_fkey')


def downgrade() -> None:
    # Rename the table back
    op.rename_table('auditlog', 'sessionlog')
    
    # Restore the original foreign key constraint names
    op.execute('ALTER TABLE sessionlog RENAME CONSTRAINT auditlog_pkey TO sessionlog_pkey')
    op.execute('ALTER TABLE sessionlog RENAME CONSTRAINT auditlog_session_id_fkey TO sessionlog_session_id_fkey')
    op.execute('ALTER TABLE sessionlog RENAME CONSTRAINT auditlog_workitem_id_fkey TO sessionlog_workitem_id_fkey')
