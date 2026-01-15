"""add external expert fields to expert_profiles

Revision ID: 50c39ba1bcd1
Revises: 328ed2e13cb1
Create Date: 2026-01-15 01:35:44.274927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '50c39ba1bcd1'
down_revision: Union[str, Sequence[str], None] = '328ed2e13cb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add external expert fields to expert_profiles table."""
    op.add_column('expert_profiles', sa.Column('external_id', sa.String(length=255), nullable=True))
    op.add_column('expert_profiles', sa.Column('external_source', sa.String(length=50), nullable=True))
    op.add_column('expert_profiles', sa.Column('external_url', sa.String(length=1000), nullable=True))
    op.add_column('expert_profiles', sa.Column('external_name', sa.String(length=255), nullable=True))
    op.add_column('expert_profiles', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('expert_profiles', sa.Column('skills', sa.Text(), nullable=True))
    op.add_column('expert_profiles', sa.Column('avatar_url', sa.String(length=1000), nullable=True))
    op.add_column('expert_profiles', sa.Column('category', sa.String(length=50), nullable=True))
    op.add_column('expert_profiles', sa.Column('is_available', sa.Boolean(), nullable=True, server_default='true'))
    op.alter_column('expert_profiles', 'user_id', existing_type=sa.INTEGER(), nullable=True)
    op.create_index(op.f('ix_expert_profiles_external_id'), 'expert_profiles', ['external_id'], unique=False)


def downgrade() -> None:
    """Remove external expert fields from expert_profiles table."""
    op.drop_index(op.f('ix_expert_profiles_external_id'), table_name='expert_profiles')
    op.alter_column('expert_profiles', 'user_id', existing_type=sa.INTEGER(), nullable=False)
    op.drop_column('expert_profiles', 'is_available')
    op.drop_column('expert_profiles', 'category')
    op.drop_column('expert_profiles', 'avatar_url')
    op.drop_column('expert_profiles', 'skills')
    op.drop_column('expert_profiles', 'bio')
    op.drop_column('expert_profiles', 'external_name')
    op.drop_column('expert_profiles', 'external_url')
    op.drop_column('expert_profiles', 'external_source')
    op.drop_column('expert_profiles', 'external_id')
