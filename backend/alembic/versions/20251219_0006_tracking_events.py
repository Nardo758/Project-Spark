"""add tracking events table

Revision ID: 20251219_0006
Revises: 20251219_0005
Create Date: 2025-12-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20251219_0006"
down_revision = "20251219_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tracking_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=True),
        sa.Column("referrer", sa.String(length=500), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("anonymous_id", sa.String(length=64), nullable=True),
        sa.Column("properties", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_tracking_events_id", "tracking_events", ["id"])
    op.create_index("ix_tracking_events_name", "tracking_events", ["name"])
    op.create_index("ix_tracking_events_path", "tracking_events", ["path"])
    op.create_index("ix_tracking_events_user_id", "tracking_events", ["user_id"])
    op.create_index("ix_tracking_events_anonymous_id", "tracking_events", ["anonymous_id"])
    op.create_index("ix_tracking_events_created_at", "tracking_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_tracking_events_created_at", table_name="tracking_events")
    op.drop_index("ix_tracking_events_anonymous_id", table_name="tracking_events")
    op.drop_index("ix_tracking_events_user_id", table_name="tracking_events")
    op.drop_index("ix_tracking_events_path", table_name="tracking_events")
    op.drop_index("ix_tracking_events_name", table_name="tracking_events")
    op.drop_index("ix_tracking_events_id", table_name="tracking_events")
    op.drop_table("tracking_events")

