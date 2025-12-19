"""add idea validations table

Revision ID: 20251219_0003
Revises: 20251219_0002
Create Date: 2025-12-19

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251219_0003"
down_revision = "20251219_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "idea_validations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("idea", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=True),
        sa.Column("amount_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending_payment",
                "paid",
                "processing",
                "completed",
                "failed",
                name="ideavalidationstatus",
            ),
            nullable=False,
            server_default="pending_payment",
        ),
        sa.Column("result_json", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("opportunity_score", sa.Integer(), nullable=True),
        sa.Column("summary", sa.String(length=255), nullable=True),
        sa.Column("competition_level", sa.String(length=50), nullable=True),
        sa.Column("urgency_level", sa.String(length=50), nullable=True),
        sa.Column("market_size_estimate", sa.String(length=100), nullable=True),
        sa.Column("validation_confidence", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_idea_validations_user_id", "idea_validations", ["user_id"], unique=False)
    op.create_index(
        "ix_idea_validations_payment_intent_id",
        "idea_validations",
        ["stripe_payment_intent_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_idea_validations_payment_intent_id", table_name="idea_validations")
    op.drop_index("ix_idea_validations_user_id", table_name="idea_validations")
    op.drop_table("idea_validations")
    op.execute("DROP TYPE IF EXISTS ideavalidationstatus")

