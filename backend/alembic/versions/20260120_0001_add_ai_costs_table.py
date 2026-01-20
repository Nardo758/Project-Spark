"""Add AI costs tracking table

Revision ID: 20260120_0001
Revises: 20260119_0002
Create Date: 2026-01-20

"""
from alembic import op
import sqlalchemy as sa

revision = '20260120_0001'
down_revision = '20260119_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ai_costs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=True),
        sa.Column('output_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('feature', sa.String(100), nullable=True),
        sa.Column('action', sa.String(100), nullable=True),
        sa.Column('request_metadata', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_ai_costs_user_id', 'ai_costs', ['user_id'])
    op.create_index('ix_ai_costs_provider', 'ai_costs', ['provider'])
    op.create_index('ix_ai_costs_model', 'ai_costs', ['model'])
    op.create_index('ix_ai_costs_feature', 'ai_costs', ['feature'])
    op.create_index('ix_ai_costs_session_id', 'ai_costs', ['session_id'])
    op.create_index('ix_ai_costs_created_at', 'ai_costs', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_ai_costs_created_at')
    op.drop_index('ix_ai_costs_session_id')
    op.drop_index('ix_ai_costs_feature')
    op.drop_index('ix_ai_costs_model')
    op.drop_index('ix_ai_costs_provider')
    op.drop_index('ix_ai_costs_user_id')
    op.drop_table('ai_costs')
