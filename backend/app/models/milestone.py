"""
Milestone Model

Tracks project milestones for success-fee agreements and expert engagements.
Enables milestone-based payments and progress tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class MilestoneStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class Milestone(Base):
    """
    Milestone for tracking project progress and triggering payments.
    
    Tied to a success-fee agreement or expert booking.
    """
    
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    
    agreement_id = Column(Integer, ForeignKey("success_fee_agreements.id", ondelete="CASCADE"), nullable=True, index=True)
    booking_id = Column(Integer, ForeignKey("expert_bookings.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expert_id = Column(Integer, ForeignKey("experts.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    order_index = Column(Integer, default=0)
    
    status = Column(Enum(MilestoneStatus), nullable=False, default=MilestoneStatus.PENDING)
    
    payment_amount_cents = Column(Integer, nullable=True)
    payment_percentage_bps = Column(Integer, nullable=True)
    
    due_date = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    deliverables = Column(Text, nullable=True)
    approval_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    approved_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_transfer_id = Column(String(255), nullable=True)
    
    metadata_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    agreement = relationship("SuccessFeeAgreement", foreign_keys=[agreement_id])
    user = relationship("User", foreign_keys=[user_id])
    expert = relationship("Expert", foreign_keys=[expert_id])
    approver = relationship("User", foreign_keys=[approved_by_user_id])
