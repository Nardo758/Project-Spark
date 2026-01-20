"""add ai_costs table

Revision ID: 20260120_0001
Revises: 20260119_0002
Create Date: 2026-01-20

"""

from alembic import op
import sqlalchemy as sa


revision = "20260120_0001"
down_revision = "20260119_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_costs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("endpoint", sa.String(length=100), nullable=True),
        sa.Column("task_type", sa.String(length=100), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("cost_usd", sa.Numeric(10, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.create_index("ix_ai_costs_user_id", "ai_costs", ["user_id"], unique=False)
    op.create_index("ix_ai_costs_provider", "ai_costs", ["provider"], unique=False)
    op.create_index("ix_ai_costs_created_at", "ai_costs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_costs_created_at", table_name="ai_costs")
    op.drop_index("ix_ai_costs_provider", table_name="ai_costs")
    op.drop_index("ix_ai_costs_user_id", table_name="ai_costs")
    op.drop_table("ai_costs")
