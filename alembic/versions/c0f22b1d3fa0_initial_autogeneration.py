"""Initial autogeneration

Revision ID: c0f22b1d3fa0
Revises: 
Create Date: 2024-10-11 09:32:41.015254

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel # added

# revision identifiers, used by Alembic.
revision: str = 'c0f22b1d3fa0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accesstoken',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('access_token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accesstoken_access_token'), 'accesstoken', ['access_token'], unique=True)
    op.create_index(op.f('ix_accesstoken_identifier'), 'accesstoken', ['identifier'], unique=True)
    op.create_table('credential',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('resource',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('fqdn', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('capabilities', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('available', sa.Boolean(), nullable=False),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('systemlog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('level', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('workqueue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('process',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('requirements', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('target_type', sa.Enum('PYTHON', 'BLUE_PRISM', 'UI_PATH', 'POWER_AUTOMATE_DESKTOP', name='targettypeenum'), nullable=True),
    sa.Column('target_source', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('target_credentials_id', sa.Integer(), nullable=True),
    sa.Column('credentials_id', sa.Integer(), nullable=True),
    sa.Column('workqueue_id', sa.Integer(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['credentials_id'], ['credential.id'], ),
    sa.ForeignKeyConstraint(['target_credentials_id'], ['credential.id'], ),
    sa.ForeignKeyConstraint(['workqueue_id'], ['workqueue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('workitem',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('reference', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('locked', sa.Boolean(), nullable=False),
    sa.Column('status', sa.Enum('NEW', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PENDING_USER_ACTION', name='workitemstatus'), nullable=False),
    sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('workqueue_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['workqueue_id'], ['workqueue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('process_id', sa.Integer(), nullable=False),
    sa.Column('resource_id', sa.Integer(), nullable=True),
    sa.Column('dispatched_at', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('NEW', 'IN_PROGRESS', 'COMPLETED', 'FAILED', name='sessionstatus'), nullable=False),
    sa.Column('stop_requested', sa.Boolean(), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['process_id'], ['process.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('trigger',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('CRON', 'WORKQUEUE', 'DATE', name='triggertype'), nullable=False),
    sa.Column('cron', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('workqueue_id', sa.Integer(), nullable=True),
    sa.Column('workqueue_resource_limit', sa.Integer(), nullable=False),
    sa.Column('workqueue_scale_up_threshold', sa.Integer(), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('enabled', sa.Boolean(), nullable=True),
    sa.Column('last_triggered', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('process_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['process_id'], ['process.id'], ),
    sa.ForeignKeyConstraint(['workqueue_id'], ['workqueue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sessionlog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('workitem_id', sa.Integer(), nullable=True),
    sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['session.id'], ),
    sa.ForeignKeyConstraint(['workitem_id'], ['workitem.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sessionlog')
    op.drop_table('trigger')
    op.drop_table('session')
    op.drop_table('workitem')
    op.drop_table('process')
    op.drop_table('workqueue')
    op.drop_table('systemlog')
    op.drop_table('resource')
    op.drop_table('credential')
    op.drop_index(op.f('ix_accesstoken_identifier'), table_name='accesstoken')
    op.drop_index(op.f('ix_accesstoken_access_token'), table_name='accesstoken')
    op.drop_table('accesstoken')
    # ### end Alembic commands ###
