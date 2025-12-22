"""add data source configs

Revision ID: 20251222_0001
Revises: 20251221_0001
Create Date: 2025-12-22

Adds admin-managed configuration for inbound webhook data sources:
- enable/disable per source
- per-source rate limits
- optional per-source HMAC secrets (fallback remains env vars)
"""

from alembic import op
import sqlalchemy as sa


revision = "20251222_0001"
down_revision = "20251221_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_source_configs",
        sa.Column("source", sa.String(length=50), primary_key=True),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("hmac_secret", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Seed defaults for known sources (secrets intentionally null).
    op.bulk_insert(
        sa.table(
            "data_source_configs",
            sa.column("source", sa.String),
            sa.column("display_name", sa.String),
            sa.column("is_enabled", sa.Boolean),
            sa.column("rate_limit_per_minute", sa.Integer),
        ),
        [
            {"source": "google_maps", "display_name": "Google Maps", "is_enabled": True, "rate_limit_per_minute": 100},
            {"source": "yelp", "display_name": "Yelp", "is_enabled": True, "rate_limit_per_minute": 100},
            {"source": "reddit", "display_name": "Reddit", "is_enabled": True, "rate_limit_per_minute": 100},
            {"source": "twitter", "display_name": "Twitter / X", "is_enabled": True, "rate_limit_per_minute": 100},
            {"source": "nextdoor", "display_name": "Nextdoor", "is_enabled": True, "rate_limit_per_minute": 100},
            {"source": "custom", "display_name": "Custom", "is_enabled": True, "rate_limit_per_minute": 100},
        ],
    )


def downgrade() -> None:
    op.drop_table("data_source_configs")

