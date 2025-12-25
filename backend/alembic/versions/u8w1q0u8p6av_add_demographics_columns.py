"""Add demographics and search_trends columns to opportunities

Revision ID: u8w1q0u8p6av
Revises: 
Create Date: 2024-12-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'u8w1q0u8p6av'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('opportunities', sa.Column('demographics', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('opportunities', sa.Column('search_trends', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('opportunities', sa.Column('demographics_fetched_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column('opportunities', 'demographics_fetched_at')
    op.drop_column('opportunities', 'search_trends')
    op.drop_column('opportunities', 'demographics')
