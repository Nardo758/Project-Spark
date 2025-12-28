"""add_purchased_reports_tables

Revision ID: 328ed2e13cb1
Revises: 20c89abc458b
Create Date: 2025-12-28 19:01:55.974293

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '328ed2e13cb1'
down_revision: Union[str, Sequence[str], None] = '20c89abc458b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create purchased reports tables."""
    op.create_table('consultant_licenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount_paid', sa.Integer(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('opportunities_used', sa.Integer(), nullable=True),
        sa.Column('max_opportunities', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('purchased_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_consultant_licenses_id'), 'consultant_licenses', ['id'], unique=False)
    
    op.create_table('purchased_bundles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=False),
        sa.Column('bundle_type', sa.String(length=100), nullable=False),
        sa.Column('amount_paid', sa.Integer(), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('purchased_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchased_bundles_id'), 'purchased_bundles', ['id'], unique=False)
    
    op.create_table('purchased_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=100), nullable=False),
        sa.Column('purchase_type', sa.String(length=50), nullable=False, server_default='individual'),
        sa.Column('bundle_id', sa.String(length=100), nullable=True),
        sa.Column('amount_paid', sa.Integer(), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('is_generated', sa.Boolean(), nullable=True),
        sa.Column('generated_report_id', sa.Integer(), nullable=True),
        sa.Column('purchased_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['generated_report_id'], ['generated_reports.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchased_reports_id'), 'purchased_reports', ['id'], unique=False)


def downgrade() -> None:
    """Drop purchased reports tables."""
    op.drop_index(op.f('ix_purchased_reports_id'), table_name='purchased_reports')
    op.drop_table('purchased_reports')
    op.drop_index(op.f('ix_purchased_bundles_id'), table_name='purchased_bundles')
    op.drop_table('purchased_bundles')
    op.drop_index(op.f('ix_consultant_licenses_id'), table_name='consultant_licenses')
    op.drop_table('consultant_licenses')
