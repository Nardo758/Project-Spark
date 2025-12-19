"""
Expert Booking Model

Tracks expert sessions, engagements, and service bookings.
Part of the Expert API Gateway functionality.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class BookingType(str, enum.Enum):
    SESSION = "session"
    PROJECT = "project"
    RETAINER = "retainer"
    QUICK_CONSULT = "quick_consult"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentModel(str, enum.Enum):
    HOURLY = "hourly"
    FIXED = "fixed"
    SUCCESS_FEE = "success_fee"
    HYBRID = "hybrid"


class ExpertBooking(Base):
    """
    Expert booking / engagement record.
    
    Tracks the full lifecycle of an expert engagement:
    - Initial quote and booking
    - Payment processing
    - Delivery and completion
    - Rating and feedback
    """
    
    __tablename__ = "expert_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expert_id = Column(Integer, ForeignKey("experts.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True, index=True)
    agreement_id = Column(Integer, ForeignKey("success_fee_agreements.id", ondelete="SET NULL"), nullable=True)
    
    booking_type = Column(Enum(BookingType), nullable=False, default=BookingType.SESSION)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    payment_model = Column(Enum(PaymentModel), nullable=False, default=PaymentModel.FIXED)
    
    quoted_amount_cents = Column(Integer, nullable=True)
    hourly_rate_cents = Column(Integer, nullable=True)
    estimated_hours = Column(Numeric(6, 2), nullable=True)
    
    success_fee_percentage_bps = Column(Integer, nullable=True)
    success_fee_cap_cents = Column(Integer, nullable=True)
    
    final_amount_cents = Column(Integer, nullable=True)
    platform_fee_cents = Column(Integer, nullable=True)
    expert_payout_cents = Column(Integer, nullable=True)
    
    currency = Column(String(10), default="usd")
    
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    user_rating = Column(Integer, nullable=True)
    user_review = Column(Text, nullable=True)
    expert_notes = Column(Text, nullable=True)
    
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_transfer_id = Column(String(255), nullable=True)
    
    meeting_url = Column(String(1000), nullable=True)
    
    deliverables = Column(Text, nullable=True)
    
    metadata_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
    expert = relationship("Expert", foreign_keys=[expert_id])
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id])
    agreement = relationship("SuccessFeeAgreement", foreign_keys=[agreement_id])
