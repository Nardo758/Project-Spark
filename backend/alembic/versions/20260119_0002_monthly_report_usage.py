"""Add monthly report usage tracking table

Revision ID: 20260119_0002
Revises: 20260119_0001
Create Date: 2026-01-19

"""
from alembic import op
import sqlalchemy as sa

revision = '20260119_0002'
down_revision = '20260119_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'monthly_report_usage',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('year_month', sa.String(7), nullable=False),
        sa.Column('reports_used', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_unique_constraint('uq_user_year_month', 'monthly_report_usage', ['user_id', 'year_month'])
    op.create_index('ix_monthly_report_usage_user_id', 'monthly_report_usage', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_monthly_report_usage_user_id')
    op.drop_constraint('uq_user_year_month', 'monthly_report_usage')
    op.drop_table('monthly_report_usage')
