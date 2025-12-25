"""add_global_copilot_tables

Revision ID: 19f70e25a1a2
Revises: 2451e7645baa
Create Date: 2025-12-25 02:23:23.817154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '19f70e25a1a2'
down_revision: Union[str, Sequence[str], None] = '2451e7645baa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add global copilot tables."""
    op.create_table('copilot_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('suggestion_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('page_context', sa.String(length=100), nullable=True),
        sa.Column('opportunity_id', sa.Integer(), nullable=True),
        sa.Column('is_dismissed', sa.Boolean(), nullable=True),
        sa.Column('is_acted_on', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_copilot_suggestions_id'), 'copilot_suggestions', ['id'], unique=False)
    op.create_index(op.f('ix_copilot_suggestions_user_id'), 'copilot_suggestions', ['user_id'], unique=False)
    
    op.create_table('global_chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('page_context', sa.String(length=100), nullable=True),
        sa.Column('opportunity_id', sa.Integer(), nullable=True),
        sa.Column('is_suggestion', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_global_chat_messages_id'), 'global_chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_global_chat_messages_user_id'), 'global_chat_messages', ['user_id'], unique=False)
    op.create_index('ix_global_chat_user_created', 'global_chat_messages', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    """Remove global copilot tables."""
    op.drop_index('ix_global_chat_user_created', table_name='global_chat_messages')
    op.drop_index(op.f('ix_global_chat_messages_user_id'), table_name='global_chat_messages')
    op.drop_index(op.f('ix_global_chat_messages_id'), table_name='global_chat_messages')
    op.drop_table('global_chat_messages')
    op.drop_index(op.f('ix_copilot_suggestions_user_id'), table_name='copilot_suggestions')
    op.drop_index(op.f('ix_copilot_suggestions_id'), table_name='copilot_suggestions')
    op.drop_table('copilot_suggestions')
