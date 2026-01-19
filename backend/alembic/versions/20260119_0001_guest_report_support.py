"""Add guest report support - nullable user_id and new report types

Revision ID: 20260119_0001
Revises: f3c9e8d7a123
Create Date: 2026-01-19

"""
from alembic import op
import sqlalchemy as sa

revision = '20260119_0001'
down_revision = 'f3c9e8d7a123'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('generated_reports', 'user_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)

    new_enum_values = [
        'feasibility',
        'strategic',
        'pestle',
        'pestle_analysis',
        'business_plan',
        'financial',
        'financial_model',
        'pitch_deck',
        'layer_1_overview',
        'layer_2_deep_dive',
        'layer_3_execution'
    ]
    
    for value in new_enum_values:
        op.execute(f"ALTER TYPE reporttype ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    op.alter_column('generated_reports', 'user_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)
