"""Add mapping and webhook tables

Revision ID: 719faccc392e
Revises: 20251221_0001
Create Date: 2025-12-21 17:56:20.641475

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '719faccc392e'
down_revision: Union[str, Sequence[str], None] = '20251221_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('map_layers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('layer_name', sa.String(length=100), nullable=False),
    sa.Column('layer_type', sa.String(length=50), nullable=False),
    sa.Column('data_source', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('style_spec', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('filter_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('display_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_map_layers_data_source'), 'map_layers', ['data_source'], unique=False)
    op.create_index(op.f('ix_map_layers_id'), 'map_layers', ['id'], unique=False)
    op.create_index(op.f('ix_map_layers_layer_name'), 'map_layers', ['layer_name'], unique=True)
    
    op.create_table('scraped_sources',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('external_id', sa.String(length=255), nullable=True),
    sa.Column('source_type', sa.String(length=50), nullable=False),
    sa.Column('scrape_id', sa.String(length=255), nullable=True),
    sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('processed', sa.Integer(), nullable=False),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraped_sources_external_id'), 'scraped_sources', ['external_id'], unique=False)
    op.create_index(op.f('ix_scraped_sources_id'), 'scraped_sources', ['id'], unique=False)
    op.create_index(op.f('ix_scraped_sources_scrape_id'), 'scraped_sources', ['scrape_id'], unique=False)
    op.create_index(op.f('ix_scraped_sources_source_type'), 'scraped_sources', ['source_type'], unique=False)
    
    op.create_table('geographic_features',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('geojson', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('feature_type', sa.String(length=50), nullable=False),
    sa.Column('location_name', sa.String(length=500), nullable=True),
    sa.Column('city', sa.String(length=255), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('postal_code', sa.String(length=20), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['source_id'], ['scraped_sources.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_geographic_features_city'), 'geographic_features', ['city'], unique=False)
    op.create_index(op.f('ix_geographic_features_id'), 'geographic_features', ['id'], unique=False)
    op.create_index(op.f('ix_geographic_features_latitude'), 'geographic_features', ['latitude'], unique=False)
    op.create_index(op.f('ix_geographic_features_longitude'), 'geographic_features', ['longitude'], unique=False)
    op.create_index(op.f('ix_geographic_features_source_id'), 'geographic_features', ['source_id'], unique=False)
    
    op.create_table('user_map_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('session_name', sa.String(length=255), nullable=True),
    sa.Column('layer_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('viewport', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_map_sessions_id'), 'user_map_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_user_map_sessions_user_id'), 'user_map_sessions', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_map_sessions_user_id'), table_name='user_map_sessions')
    op.drop_index(op.f('ix_user_map_sessions_id'), table_name='user_map_sessions')
    op.drop_table('user_map_sessions')
    
    op.drop_index(op.f('ix_geographic_features_source_id'), table_name='geographic_features')
    op.drop_index(op.f('ix_geographic_features_longitude'), table_name='geographic_features')
    op.drop_index(op.f('ix_geographic_features_latitude'), table_name='geographic_features')
    op.drop_index(op.f('ix_geographic_features_id'), table_name='geographic_features')
    op.drop_index(op.f('ix_geographic_features_city'), table_name='geographic_features')
    op.drop_table('geographic_features')
    
    op.drop_index(op.f('ix_scraped_sources_source_type'), table_name='scraped_sources')
    op.drop_index(op.f('ix_scraped_sources_scrape_id'), table_name='scraped_sources')
    op.drop_index(op.f('ix_scraped_sources_id'), table_name='scraped_sources')
    op.drop_index(op.f('ix_scraped_sources_external_id'), table_name='scraped_sources')
    op.drop_table('scraped_sources')
    
    op.drop_index(op.f('ix_map_layers_layer_name'), table_name='map_layers')
    op.drop_index(op.f('ix_map_layers_id'), table_name='map_layers')
    op.drop_index(op.f('ix_map_layers_data_source'), table_name='map_layers')
    op.drop_table('map_layers')
