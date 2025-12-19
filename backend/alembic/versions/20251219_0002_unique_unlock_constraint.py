"""add unique constraint to unlocked opportunities

Revision ID: 20251219_0002
Revises: 20251219_0001
Create Date: 2025-12-19

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "20251219_0002"
down_revision = "20251219_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_unlocked_opportunity_user_opportunity",
        "unlocked_opportunities",
        ["user_id", "opportunity_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_unlocked_opportunity_user_opportunity",
        "unlocked_opportunities",
        type_="unique",
    )

