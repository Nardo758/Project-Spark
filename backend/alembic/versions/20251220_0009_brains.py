"""add brains table

Revision ID: 20251220_0009
Revises: 20251219_0008
Create Date: 2025-12-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20251220_0009"
down_revision = "20251219_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "brains",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("focus_tags", sa.Text(), nullable=True),
        sa.Column("match_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("knowledge_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost_usd", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_brains_user_id", "brains", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_brains_user_id", table_name="brains")
    op.drop_table("brains")

