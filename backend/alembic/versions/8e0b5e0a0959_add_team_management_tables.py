"""Add team management tables

Revision ID: 8e0b5e0a0959
Revises: 50c39ba1bcd1
Create Date: 2026-01-16 19:51:22.448717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8e0b5e0a0959'
down_revision: Union[str, Sequence[str], None] = '50c39ba1bcd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add team management tables for Business Track features."""
    from sqlalchemy.dialects.postgresql import ENUM
    
    # Create enums first
    teamrole = ENUM('OWNER', 'ADMIN', 'MEMBER', name='teamrole', create_type=False)
    invitestatus = ENUM('PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED', name='invitestatus', create_type=False)
    
    op.execute("CREATE TYPE teamrole AS ENUM ('OWNER', 'ADMIN', 'MEMBER')")
    op.execute("CREATE TYPE invitestatus AS ENUM ('PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED')")
    
    # Create teams table
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('max_seats', sa.Integer(), nullable=True, default=3),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('api_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('api_rate_limit', sa.Integer(), nullable=True, default=100),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_slug'), 'teams', ['slug'], unique=True)
    
    # Create team_members table
    op.create_table('team_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', teamrole, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'user_id', name='uq_team_member')
    )
    op.create_index(op.f('ix_team_members_id'), 'team_members', ['id'], unique=False)
    
    # Create team_invitations table
    op.create_table('team_invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', teamrole, nullable=False),
        sa.Column('status', invitestatus, nullable=False),
        sa.Column('invite_token', sa.String(length=255), nullable=False),
        sa.Column('invited_by_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accepted_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['accepted_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['invited_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'email', 'status', name='uq_team_invitation_pending')
    )
    op.create_index(op.f('ix_team_invitations_id'), 'team_invitations', ['id'], unique=False)
    op.create_index(op.f('ix_team_invitations_email'), 'team_invitations', ['email'], unique=False)
    op.create_index(op.f('ix_team_invitations_invite_token'), 'team_invitations', ['invite_token'], unique=True)
    
    # Create team_api_keys table
    op.create_table('team_api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('key_prefix', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True, default=0),
        sa.Column('scopes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_team_api_keys_id'), 'team_api_keys', ['id'], unique=False)
    op.create_index(op.f('ix_team_api_keys_key_hash'), 'team_api_keys', ['key_hash'], unique=True)


def downgrade() -> None:
    """Remove team management tables."""
    op.drop_index(op.f('ix_team_api_keys_key_hash'), table_name='team_api_keys')
    op.drop_index(op.f('ix_team_api_keys_id'), table_name='team_api_keys')
    op.drop_table('team_api_keys')
    
    op.drop_index(op.f('ix_team_invitations_invite_token'), table_name='team_invitations')
    op.drop_index(op.f('ix_team_invitations_email'), table_name='team_invitations')
    op.drop_index(op.f('ix_team_invitations_id'), table_name='team_invitations')
    op.drop_table('team_invitations')
    
    op.drop_index(op.f('ix_team_members_id'), table_name='team_members')
    op.drop_table('team_members')
    
    op.drop_index(op.f('ix_teams_slug'), table_name='teams')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')
    
    op.execute("DROP TYPE invitestatus")
    op.execute("DROP TYPE teamrole")
