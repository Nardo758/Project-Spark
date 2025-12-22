"""add consultant studio tables

Revision ID: 20251221_0001
Revises: 0d02a1dd6502
Create Date: 2025-12-21

Creates tables for Enhanced Consultant Studio:
- consultant_activity: tracks user interactions
- detected_trends: stores AI-detected market trends
- trend_opportunity_mapping: links trends to opportunities
- location_analysis_cache: caches location analyses
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime, timedelta


revision = '20251221_0001'
down_revision = '0d02a1dd6502'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'consultant_activity',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('path', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=True),
        sa.Column('result_summary', sa.Text(), nullable=True),
        sa.Column('ai_model_used', sa.String(length=50), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_consultant_activity_id', 'consultant_activity', ['id'])
    op.create_index('ix_consultant_activity_user_id', 'consultant_activity', ['user_id'])
    op.create_index('ix_consultant_activity_session_id', 'consultant_activity', ['session_id'])
    op.create_index('ix_consultant_activity_path', 'consultant_activity', ['path'])
    op.create_index('ix_consultant_activity_created_at', 'consultant_activity', ['created_at'])

    op.create_table(
        'detected_trends',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('trend_name', sa.String(length=255), nullable=False),
        sa.Column('trend_strength', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('keywords', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=True),
        sa.Column('opportunities_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('growth_rate', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Integer(), nullable=True),
        sa.Column('ai_signature', postgresql.JSONB(), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_detected_trends_id', 'detected_trends', ['id'])
    op.create_index('ix_detected_trends_trend_name', 'detected_trends', ['trend_name'])
    op.create_index('ix_detected_trends_category', 'detected_trends', ['category'])
    op.create_index('ix_detected_trends_detected_at', 'detected_trends', ['detected_at'])

    op.create_table(
        'trend_opportunity_mapping',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('trend_id', sa.Integer(), sa.ForeignKey('detected_trends.id', ondelete='CASCADE'), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), sa.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('relationship_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('mapped_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('trend_id', 'opportunity_id', name='uq_trend_opportunity'),
    )
    op.create_index('ix_trend_opportunity_mapping_id', 'trend_opportunity_mapping', ['id'])
    op.create_index('ix_trend_opportunity_mapping_trend_id', 'trend_opportunity_mapping', ['trend_id'])
    op.create_index('ix_trend_opportunity_mapping_opportunity_id', 'trend_opportunity_mapping', ['opportunity_id'])

    op.create_table(
        'location_analysis_cache',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('cache_key', sa.String(length=255), nullable=False, unique=True),
        sa.Column('city', sa.String(length=255), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('business_type', sa.String(length=50), nullable=False),
        sa.Column('business_subtype', sa.String(length=100), nullable=True),
        sa.Column('query_params', postgresql.JSONB(), nullable=True),
        sa.Column('geojson_snapshot', postgresql.JSONB(), nullable=True),
        sa.Column('demographic_data', postgresql.JSONB(), nullable=True),
        sa.Column('market_metrics', postgresql.JSONB(), nullable=True),
        sa.Column('claude_summary', sa.Text(), nullable=True),
        sa.Column('site_recommendations', postgresql.JSONB(), nullable=True),
        sa.Column('hit_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_location_analysis_cache_id', 'location_analysis_cache', ['id'])
    op.create_index('ix_location_analysis_cache_cache_key', 'location_analysis_cache', ['cache_key'])
    op.create_index('ix_location_analysis_cache_city', 'location_analysis_cache', ['city'])
    op.create_index('ix_location_analysis_cache_business_type', 'location_analysis_cache', ['business_type'])
    op.create_index('ix_location_analysis_cache_expires_at', 'location_analysis_cache', ['expires_at'])


def downgrade() -> None:
    op.drop_index('ix_location_analysis_cache_expires_at', table_name='location_analysis_cache')
    op.drop_index('ix_location_analysis_cache_business_type', table_name='location_analysis_cache')
    op.drop_index('ix_location_analysis_cache_city', table_name='location_analysis_cache')
    op.drop_index('ix_location_analysis_cache_cache_key', table_name='location_analysis_cache')
    op.drop_index('ix_location_analysis_cache_id', table_name='location_analysis_cache')
    op.drop_table('location_analysis_cache')

    op.drop_index('ix_trend_opportunity_mapping_opportunity_id', table_name='trend_opportunity_mapping')
    op.drop_index('ix_trend_opportunity_mapping_trend_id', table_name='trend_opportunity_mapping')
    op.drop_index('ix_trend_opportunity_mapping_id', table_name='trend_opportunity_mapping')
    op.drop_table('trend_opportunity_mapping')

    op.drop_index('ix_detected_trends_detected_at', table_name='detected_trends')
    op.drop_index('ix_detected_trends_category', table_name='detected_trends')
    op.drop_index('ix_detected_trends_trend_name', table_name='detected_trends')
    op.drop_index('ix_detected_trends_id', table_name='detected_trends')
    op.drop_table('detected_trends')

    op.drop_index('ix_consultant_activity_created_at', table_name='consultant_activity')
    op.drop_index('ix_consultant_activity_path', table_name='consultant_activity')
    op.drop_index('ix_consultant_activity_session_id', table_name='consultant_activity')
    op.drop_index('ix_consultant_activity_user_id', table_name='consultant_activity')
    op.drop_index('ix_consultant_activity_id', table_name='consultant_activity')
    op.drop_table('consultant_activity')
