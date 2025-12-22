"""add_unique_constraint_scraped_sources

Revision ID: 2451e7645baa
Revises: 719faccc392e
Create Date: 2025-12-21 18:50:51.913052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2451e7645baa'
down_revision: Union[str, Sequence[str], None] = 'add_rate_limit_counters'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint on (source_type, external_id) for deduplication."""
    op.create_index(
        'ix_scraped_sources_source_external_id',
        'scraped_sources',
        ['source_type', 'external_id'],
        unique=True,
        postgresql_where=sa.text('external_id IS NOT NULL')
    )


def downgrade() -> None:
    """Remove unique constraint."""
    op.drop_index('ix_scraped_sources_source_external_id', table_name='scraped_sources')
