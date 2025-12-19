"""bootstrap full schema via SQLAlchemy metadata

Revision ID: 20251219_0004
Revises: 20251219_0003
Create Date: 2025-12-19

This migration creates any missing tables using SQLAlchemy's metadata. It exists
to support clean provisioning in new environments now that we rely on Alembic
instead of runtime `create_all()`.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "20251219_0004"
down_revision = "20251219_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure models are registered on Base.metadata.
    import app.models  # noqa: F401
    from app.db.database import Base

    bind = op.get_bind()
    inspector = inspect(bind)
    existing = set(inspector.get_table_names())

    missing_tables = [t for name, t in Base.metadata.tables.items() if name not in existing]
    if missing_tables:
        Base.metadata.create_all(bind=bind, tables=missing_tables)


def downgrade() -> None:
    # No-op: we don't attempt to drop the entire schema automatically.
    pass

