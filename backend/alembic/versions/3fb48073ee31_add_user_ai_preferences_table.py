"""Add user_ai_preferences table

Revision ID: 3fb48073ee31
Revises: 20260119_0002
Create Date: 2026-01-21 15:48:36.261528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '3fb48073ee31'
down_revision: Union[str, Sequence[str], None] = '20260119_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_ai_preferences table for Dual-Realm Workspace AI provider settings."""
    op.create_table('user_ai_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=True, server_default='claude'),
        sa.Column('mode', sa.String(length=50), nullable=True, server_default='replit'),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('encrypted_openai_api_key', sa.Text(), nullable=True),
        sa.Column('openai_key_validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_ai_preferences_id'), 'user_ai_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_user_ai_preferences_user_id'), 'user_ai_preferences', ['user_id'], unique=True)


def downgrade() -> None:
    """Drop user_ai_preferences table."""
    op.drop_index(op.f('ix_user_ai_preferences_user_id'), table_name='user_ai_preferences')
    op.drop_index(op.f('ix_user_ai_preferences_id'), table_name='user_ai_preferences')
    op.drop_table('user_ai_preferences')
