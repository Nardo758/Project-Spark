from __future__ import annotations

import enum

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class StripeWebhookEventStatus(str, enum.Enum):
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class StripeWebhookEvent(Base):
    """
    Stripe webhook idempotency + observability table.

    We use Stripe's event id (evt_*) as a unique key so retries can't
    double-fulfill side effects.
    """

    __tablename__ = "stripe_webhook_events"

    id = Column(Integer, primary_key=True, index=True)

    stripe_event_id = Column(String(255), nullable=False, unique=True, index=True)
    event_type = Column(String(255), nullable=False)
    livemode = Column(Boolean, default=False)

    status = Column(Enum(StripeWebhookEventStatus), nullable=False, default=StripeWebhookEventStatus.PROCESSING)
    attempt_count = Column(Integer, nullable=False, default=1)

    # Stripe's `created` timestamp (seconds since epoch), stored as a datetime when available
    stripe_created_at = Column(DateTime(timezone=True), nullable=True)

    received_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PayPerUnlockAttemptStatus(str, enum.Enum):
    CREATED = "created"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class PayPerUnlockAttempt(Base):
    """
    Tracks pay-per-unlock attempts so we can enforce daily limits safely.

    This is intentionally separate from UnlockedOpportunity:
    - attempts exist before payment succeeds
    - attempts can fail/cancel
    """

    __tablename__ = "pay_per_unlock_attempts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)

    attempt_date = Column(Date, nullable=False, index=True)  # UTC date bucket
    status = Column(Enum(PayPerUnlockAttemptStatus), nullable=False, default=PayPerUnlockAttemptStatus.CREATED)

    stripe_payment_intent_id = Column(String(255), nullable=True, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")
    opportunity = relationship("Opportunity")

