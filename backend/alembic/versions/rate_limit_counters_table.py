"""Add rate_limit_counters table for atomic rate limiting

Revision ID: add_rate_limit_counters
Revises: 719faccc392e
Create Date: 2024-12-21

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_rate_limit_counters'
down_revision = '719faccc392e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'rate_limit_counters',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('window_start', sa.DateTime(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_requests', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_rate_limit_source_window',
        'rate_limit_counters',
        ['source', 'window_start'],
        unique=True
    )


def downgrade():
    op.drop_index('ix_rate_limit_source_window', table_name='rate_limit_counters')
    op.drop_table('rate_limit_counters')
