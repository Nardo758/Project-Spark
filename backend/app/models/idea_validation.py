from __future__ import annotations

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class IdeaValidationStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class IdeaValidation(Base):
    __tablename__ = "idea_validations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # User input
    idea = Column(Text, nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)

    # Payment linkage (optional until created/paid)
    stripe_payment_intent_id = Column(String(255), nullable=True, unique=True, index=True)
    amount_cents = Column(Integer, nullable=True)
    currency = Column(String(10), default="usd")

    status = Column(Enum(IdeaValidationStatus), nullable=False, default=IdeaValidationStatus.PENDING_PAYMENT)

    # Result data (JSON-in-Text)
    result_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Useful denormalized fields for querying
    opportunity_score = Column(Integer, nullable=True)
    summary = Column(String(255), nullable=True)
    competition_level = Column(String(50), nullable=True)
    urgency_level = Column(String(50), nullable=True)
    market_size_estimate = Column(String(100), nullable=True)
    validation_confidence = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")

