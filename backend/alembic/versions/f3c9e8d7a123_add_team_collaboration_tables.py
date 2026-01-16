"""Add team collaboration tables

Revision ID: f3c9e8d7a123
Revises: 8e0b5e0a0959
Create Date: 2026-01-16 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f3c9e8d7a123'
down_revision: Union[str, Sequence[str], None] = '8e0b5e0a0959'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create team collaboration tables."""
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE teamactivitytype AS ENUM (
                'opportunity_shared',
                'opportunity_claimed',
                'report_generated',
                'member_joined',
                'member_left',
                'member_invited',
                'comment_added',
                'note_added',
                'workspace_created'
            );
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.create_table(
        'team_opportunities',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('team_id', sa.Integer(), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('opportunity_id', sa.Integer(), sa.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('shared_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(20), default='medium'),
        sa.Column('status', sa.String(50), default='new'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    op.create_table(
        'team_opportunity_notes',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('team_opportunity_id', sa.Integer(), sa.ForeignKey('team_opportunities.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    from sqlalchemy.dialects.postgresql import ENUM
    teamactivitytype = ENUM(
        'opportunity_shared', 'opportunity_claimed', 'report_generated',
        'member_joined', 'member_left', 'member_invited', 'comment_added',
        'note_added', 'workspace_created',
        name='teamactivitytype', create_type=False
    )
    
    op.create_table(
        'team_activities',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('team_id', sa.Integer(), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('activity_type', teamactivitytype, nullable=False),
        sa.Column('actor_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('target_type', sa.String(50), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('target_title', sa.String(255), nullable=True),
        sa.Column('extra_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Drop team collaboration tables."""
    op.drop_table('team_activities')
    op.drop_table('team_opportunity_notes')
    op.drop_table('team_opportunities')
    op.execute('DROP TYPE IF EXISTS teamactivitytype')
