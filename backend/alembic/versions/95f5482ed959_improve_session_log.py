"""Improve session log

Revision ID: 95f5482ed959
Revises: 9359bc77847e
Create Date: 2025-07-23 21:05:16.525255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '95f5482ed959'
down_revision: Union[str, None] = '9359bc77847e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migrate SessionLog table from old schema to new schema.
    
    Old schema: id, session_id, workitem_id, message, created_at
    New schema: All old fields plus logging fields, nullable session_id
    """
    
    print("Starting SessionLog migration...")
    
    # Step 1: Add new columns with default values
    print("Adding new columns...")
    
    # Core logging fields
    op.add_column('sessionlog', sa.Column('level', sa.String(), nullable=False, server_default='INFO'))
    op.add_column('sessionlog', sa.Column('logger_name', sa.String(), nullable=False, server_default=''))
    
    # Source location fields (nullable since old records won't have this)
    op.add_column('sessionlog', sa.Column('module', sa.String(), nullable=True))
    op.add_column('sessionlog', sa.Column('function_name', sa.String(), nullable=True))
    op.add_column('sessionlog', sa.Column('line_number', sa.Integer(), nullable=True))
    
    # Exception fields (nullable)
    op.add_column('sessionlog', sa.Column('exception_type', sa.String(), nullable=True))
    op.add_column('sessionlog', sa.Column('exception_message', sa.Text(), nullable=True))
    op.add_column('sessionlog', sa.Column('traceback', sa.Text(), nullable=True))
    
    # Structured data for audit trail (nullable)
    op.add_column('sessionlog', sa.Column('structured_data', JSONB(), nullable=True))
    
    # Event timestamp (will populate from created_at)
    op.add_column('sessionlog', sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=True))
    
    print("New columns added successfully.")
    
    # Step 2: Populate event_timestamp from created_at for existing records
    print("Populating event_timestamp from created_at...")
    op.execute("""
        UPDATE sessionlog 
        SET event_timestamp = created_at 
        WHERE event_timestamp IS NULL
    """)
    
    # Step 3: Make session_id nullable
    print("Making session_id nullable...")
    op.alter_column('sessionlog', 'session_id', nullable=True)
    
    # Step 4: Make event_timestamp NOT NULL now that it's populated
    print("Making event_timestamp NOT NULL...")
    op.alter_column('sessionlog', 'event_timestamp', nullable=False)
    
    # Step 5: Add indexes for common query patterns
    print("Adding indexes...")
    
    # Primary composite index for session-based queries
    op.create_index(
        'idx_sessionlog_session_event', 
        'sessionlog', 
        ['session_id', 'event_timestamp']
    )
    
    # Index for workitem-based queries
    op.create_index(
        'idx_sessionlog_workitem_event', 
        'sessionlog', 
        ['workitem_id', 'event_timestamp']
    )
    
    # Index for log level filtering
    op.create_index('idx_sessionlog_level', 'sessionlog', ['level'])
    
    # Index for logger name filtering
    op.create_index('idx_sessionlog_logger', 'sessionlog', ['logger_name'])
    
    # Partial index for exception queries
    op.execute("""
        CREATE INDEX idx_sessionlog_exception 
        ON sessionlog(exception_type) 
        WHERE exception_type IS NOT NULL
    """)
    
    # GIN index for structured data queries (PostgreSQL specific)
    op.execute("""
        CREATE INDEX idx_sessionlog_structured_data 
        ON sessionlog USING GIN (structured_data)
    """)
    
    print("Indexes created successfully.")
    print("Migration completed successfully!")
    

def downgrade() -> None:
    """
    Rollback migration - remove new columns and indexes.
    WARNING: This will lose data in the new columns!
    """
    
    print("Rolling back SessionLog migration...")
    print("WARNING: This will permanently delete data in new columns!")
    
    # Drop indexes first
    op.drop_index('idx_sessionlog_structured_data', 'sessionlog')
    op.drop_index('idx_sessionlog_exception', 'sessionlog')
    op.drop_index('idx_sessionlog_logger', 'sessionlog')
    op.drop_index('idx_sessionlog_level', 'sessionlog')
    op.drop_index('idx_sessionlog_workitem_event', 'sessionlog')
    op.drop_index('idx_sessionlog_session_event', 'sessionlog')
    
   
    # Clean up rows that wouldn't be valid in the old schema
    op.execute("DELETE FROM sessionlog WHERE session_id IS NULL")
    
    # Restore session_id NOT NULL constraint
    print("Restoring session_id NOT NULL constraint...")
    op.alter_column('sessionlog', 'session_id', nullable=False)
    
    # Drop new columns
    op.drop_column('sessionlog', 'event_timestamp')
    op.drop_column('sessionlog', 'structured_data')
    op.drop_column('sessionlog', 'traceback')
    op.drop_column('sessionlog', 'exception_message')
    op.drop_column('sessionlog', 'exception_type')
    op.drop_column('sessionlog', 'line_number')
    op.drop_column('sessionlog', 'function_name')
    op.drop_column('sessionlog', 'module')
    op.drop_column('sessionlog', 'logger_name')
    op.drop_column('sessionlog', 'level')
    
    # Note: Existing FK constraints are left unchanged as they work fine with nullable columns
    
    print("Rollback completed.")