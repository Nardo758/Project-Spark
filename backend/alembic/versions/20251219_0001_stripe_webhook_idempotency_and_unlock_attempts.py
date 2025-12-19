"""stripe webhook idempotency and pay-per-unlock attempts

Revision ID: 20251219_0001
Revises: 
Create Date: 2025-12-19

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251219_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stripe_webhook_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("stripe_event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("livemode", sa.Boolean(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("processing", "processed", "failed", name="stripewebhookeventstatus"),
            nullable=False,
            server_default="processing",
        ),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("stripe_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_stripe_webhook_events_stripe_event_id", "stripe_webhook_events", ["stripe_event_id"], unique=True)

    op.create_table(
        "pay_per_unlock_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opportunity_id", sa.Integer(), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attempt_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("created", "succeeded", "failed", "canceled", name="payperunlockattemptstatus"),
            nullable=False,
            server_default="created",
        ),
        sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_pay_per_unlock_attempts_user_date",
        "pay_per_unlock_attempts",
        ["user_id", "attempt_date"],
        unique=False,
    )
    op.create_index(
        "ix_pay_per_unlock_attempts_payment_intent",
        "pay_per_unlock_attempts",
        ["stripe_payment_intent_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_pay_per_unlock_attempts_payment_intent", table_name="pay_per_unlock_attempts")
    op.drop_index("ix_pay_per_unlock_attempts_user_date", table_name="pay_per_unlock_attempts")
    op.drop_table("pay_per_unlock_attempts")

    op.drop_index("ix_stripe_webhook_events_stripe_event_id", table_name="stripe_webhook_events")
    op.drop_table("stripe_webhook_events")

    op.execute("DROP TYPE IF EXISTS payperunlockattemptstatus")
    op.execute("DROP TYPE IF EXISTS stripewebhookeventstatus")

