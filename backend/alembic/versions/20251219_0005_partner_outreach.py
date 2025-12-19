"""add partner outreach tracker

Revision ID: 20251219_0005
Revises: 20251219_0004
Create Date: 2025-12-19

Creates a small table used to track integration/tool partner outreach.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251219_0005"
down_revision = "20251219_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "partner_outreach",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("contact_name", sa.String(length=255), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "identified",
                "contacted",
                "in_talks",
                "active",
                "paused",
                "rejected",
                name="partneroutreachstatus",
            ),
            nullable=False,
            server_default="identified",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_partner_outreach_id", "partner_outreach", ["id"])
    op.create_index("ix_partner_outreach_name", "partner_outreach", ["name"])


def downgrade() -> None:
    op.drop_index("ix_partner_outreach_name", table_name="partner_outreach")
    op.drop_index("ix_partner_outreach_id", table_name="partner_outreach")
    op.drop_table("partner_outreach")
    # Note: enum type drop is intentionally omitted for safety across environments.

