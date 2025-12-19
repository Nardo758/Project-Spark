"""
Success-Fee Agreement Model

Represents a success-fee or revenue-share agreement between a user and an expert.
Tracks terms, trigger conditions, caps, and payout status.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class AgreementType(str, enum.Enum):
    SUCCESS_FEE = "success_fee"
    REVENUE_SHARE = "revenue_share"
    MILESTONE_BASED = "milestone_based"


class AgreementStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TriggerType(str, enum.Enum):
    FIRST_REVENUE = "first_revenue"
    REVENUE_THRESHOLD = "revenue_threshold"
    MILESTONE_COMPLETION = "milestone_completion"
    TIME_BASED = "time_based"
    CUSTOM = "custom"


class SuccessFeeAgreement(Base):
    """
    Success-fee / revenue-share agreement between user and expert.
    
    Supports:
    - Success fees (one-time payment on trigger)
    - Revenue share (ongoing percentage of revenue)
    - Milestone-based payments
    """
    
    __tablename__ = "success_fee_agreements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expert_id = Column(Integer, ForeignKey("experts.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True, index=True)
    
    agreement_type = Column(Enum(AgreementType), nullable=False, default=AgreementType.SUCCESS_FEE)
    status = Column(Enum(AgreementStatus), nullable=False, default=AgreementStatus.DRAFT)
    
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    fee_percentage_bps = Column(Integer, nullable=True)
    fee_cap_cents = Column(Integer, nullable=True)
    minimum_payout_cents = Column(Integer, nullable=True)
    
    trigger_type = Column(Enum(TriggerType), nullable=False, default=TriggerType.FIRST_REVENUE)
    trigger_threshold_cents = Column(Integer, nullable=True)
    trigger_conditions = Column(Text, nullable=True)
    
    payout_split_expert_bps = Column(Integer, default=7000)
    payout_split_platform_bps = Column(Integer, default=1000)
    payout_split_escrow_bps = Column(Integer, default=2000)
    
    escrow_release_days = Column(Integer, default=30)
    
    total_revenue_tracked = Column(Numeric(14, 2), default=0)
    total_payouts_made = Column(Numeric(14, 2), default=0)
    
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime(timezone=True), nullable=True)
    
    starts_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    terms_accepted_by_user = Column(Boolean, default=False)
    terms_accepted_by_expert = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)
    
    stripe_escrow_account_id = Column(String(255), nullable=True)
    
    metadata_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
    expert = relationship("Expert", foreign_keys=[expert_id])
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id])
