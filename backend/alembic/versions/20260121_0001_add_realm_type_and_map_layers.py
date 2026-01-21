"""Add realm_type to opportunities and saved_map_layers table

Revision ID: 20260121_0001
Revises: 
Create Date: 2026-01-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260121_0001'
down_revision = '3fb48073ee31'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('opportunities', sa.Column('realm_type', sa.String(20), nullable=True, server_default='both'))
    op.create_index('idx_opportunities_realm_type', 'opportunities', ['realm_type'])
    
    op.create_table(
        'saved_map_layers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), sa.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layer_type', sa.String(50), nullable=False, server_default='custom'),
        sa.Column('viewport', postgresql.JSONB(), nullable=True),
        sa.Column('layers_data', postgresql.JSONB(), nullable=True),
        sa.Column('markers', postgresql.JSONB(), nullable=True),
        sa.Column('polygons', postgresql.JSONB(), nullable=True),
        sa.Column('datasets', postgresql.JSONB(), nullable=True),
        sa.Column('summary', postgresql.JSONB(), nullable=True),
        sa.Column('is_shared', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('idx_saved_map_layers_user_id', 'saved_map_layers', ['user_id'])
    op.create_index('idx_saved_map_layers_opportunity_id', 'saved_map_layers', ['opportunity_id'])


def downgrade() -> None:
    op.drop_index('idx_saved_map_layers_opportunity_id')
    op.drop_index('idx_saved_map_layers_user_id')
    op.drop_table('saved_map_layers')
    op.drop_index('idx_opportunities_realm_type')
    op.drop_column('opportunities', 'realm_type')
