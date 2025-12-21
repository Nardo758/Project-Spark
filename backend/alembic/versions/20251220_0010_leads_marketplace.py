"""add leads marketplace tables

Revision ID: 20251220_0010
Revises: 20251220_0009
Create Date: 2025-12-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20251220_0010"
down_revision = "20251220_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=True),
        sa.Column("public_id", sa.String(length=32), nullable=False),
        sa.Column("public_title", sa.String(length=255), nullable=False),
        sa.Column("anonymized_summary", sa.Text(), nullable=False),
        sa.Column("industry", sa.String(length=120), nullable=True),
        sa.Column("deal_size_range", sa.String(length=80), nullable=True),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("revenue_range", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("lead_price_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quality_score", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("full_data_json", sa.Text(), nullable=True),
        sa.Column("views_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("purchase_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_leads_public_id", "leads", ["public_id"], unique=True)
    op.create_index("ix_leads_status", "leads", ["status"], unique=False)
    op.create_index("ix_leads_industry", "leads", ["industry"], unique=False)
    op.create_index("ix_leads_published_at", "leads", ["published_at"], unique=False)

    op.create_table(
        "lead_purchases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("buyer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("transaction_id", sa.String(length=255), nullable=True),
        sa.Column("payment_provider", sa.String(length=20), nullable=True, server_default="stripe"),
        sa.Column("payment_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("amount_paid_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("purchased_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("download_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("lead_id", "buyer_id", name="uq_lead_purchase_lead_buyer"),
    )
    op.create_index("ix_lead_purchases_lead_id", "lead_purchases", ["lead_id"], unique=False)
    op.create_index("ix_lead_purchases_buyer_id", "lead_purchases", ["buyer_id"], unique=False)

    op.create_table(
        "saved_searches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("filters_json", sa.Text(), nullable=False),
        sa.Column("notification_frequency", sa.String(length=20), nullable=False, server_default="instant"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("match_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_saved_searches_user_id", "saved_searches", ["user_id"], unique=False)

    op.create_table(
        "lead_views",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_id", sa.String(length=120), nullable=True),
        sa.Column("viewed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_lead_views_lead_id", "lead_views", ["lead_id"], unique=False)
    op.create_index("ix_lead_views_user_id", "lead_views", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_views_user_id", table_name="lead_views")
    op.drop_index("ix_lead_views_lead_id", table_name="lead_views")
    op.drop_table("lead_views")

    op.drop_index("ix_saved_searches_user_id", table_name="saved_searches")
    op.drop_table("saved_searches")

    op.drop_index("ix_lead_purchases_buyer_id", table_name="lead_purchases")
    op.drop_index("ix_lead_purchases_lead_id", table_name="lead_purchases")
    op.drop_table("lead_purchases")

    op.drop_index("ix_leads_published_at", table_name="leads")
    op.drop_index("ix_leads_industry", table_name="leads")
    op.drop_index("ix_leads_status", table_name="leads")
    op.drop_index("ix_leads_public_id", table_name="leads")
    op.drop_table("leads")

