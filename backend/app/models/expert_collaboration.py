"""
Expert Collaboration System Models

Extended models for the Expert Collaboration System:
- Expert profiles linked to users
- Engagement workflows with permission levels
- Reviews and ratings
- In-platform messaging
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Numeric, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ExpertCategory(str, enum.Enum):
    BUSINESS_CONSULTANT = "business_consultant"
    TECHNICAL_ADVISOR = "technical_advisor"
    INDUSTRY_SPECIALIST = "industry_specialist"
    GROWTH_MARKETING = "growth_marketing"
    FINANCIAL_ADVISOR = "financial_advisor"
    LEGAL_COMPLIANCE = "legal_compliance"


class ExpertSpecialization(str, enum.Enum):
    STRATEGY_PLANNING = "strategy_planning"
    MARKET_ANALYSIS = "market_analysis"
    BUSINESS_MODEL_DESIGN = "business_model_design"
    GO_TO_MARKET = "go_to_market"
    SOFTWARE_ARCHITECTURE = "software_architecture"
    PRODUCT_DEVELOPMENT = "product_development"
    TECHNICAL_DUE_DILIGENCE = "technical_due_diligence"
    CTO_AS_A_SERVICE = "cto_as_a_service"
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    SAAS = "saas"
    MARKETPLACE = "marketplace"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    SUPPLY_CHAIN = "supply_chain"
    CUSTOMER_ACQUISITION = "customer_acquisition"
    BRAND_STRATEGY = "brand_strategy"
    CONTENT_MARKETING = "content_marketing"
    PERFORMANCE_MARKETING = "performance_marketing"
    FINANCIAL_MODELING = "financial_modeling"
    FUNDRAISING = "fundraising"
    VALUATION = "valuation"
    CFO_AS_A_SERVICE = "cfo_as_a_service"
    CORPORATE_STRUCTURE = "corporate_structure"
    IP_PATENTS = "ip_patents"
    CONTRACTS = "contracts"


class ExpertStageExpertise(str, enum.Enum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    GROWTH = "growth"
    SCALE = "scale"


class EngagementType(str, enum.Enum):
    CONSULTATION = "consultation"
    PROJECT = "project"
    RETAINER = "retainer"
    HOURLY = "hourly"
    EQUITY_PARTNERSHIP = "equity_partnership"


class EngagementStatus(str, enum.Enum):
    REQUEST_SENT = "request_sent"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DECLINED = "declined"


class ExpertPermissionLevel(str, enum.Enum):
    VIEWER = "viewer"
    CONTRIBUTOR = "contributor"
    ADVISOR = "advisor"
    PARTNER = "partner"


class ExpertProfile(Base):
    """
    Extended expert profile linked to a User.
    
    Users can apply to become experts and have their profiles
    verified by the platform.
    """
    
    __tablename__ = "expert_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    expert_id = Column(Integer, ForeignKey("experts.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    timezone = Column(String(100), nullable=True)
    
    primary_category = Column(Enum(ExpertCategory), nullable=True)
    specializations = Column(Text, nullable=True)
    industries = Column(Text, nullable=True)
    stage_expertise = Column(Text, nullable=True)
    
    years_experience = Column(Integer, nullable=True)
    companies_json = Column(Text, nullable=True)
    exits = Column(Text, nullable=True)
    funded_companies = Column(Integer, default=0)
    portfolio_highlights = Column(Text, nullable=True)
    
    education = Column(String(500), nullable=True)
    certifications = Column(Text, nullable=True)
    speaking_engagements = Column(Integer, default=0)
    publications = Column(Integer, default=0)
    
    availability_description = Column(String(255), nullable=True)
    availability_hours_per_week = Column(Integer, nullable=True)
    engagement_types = Column(Text, nullable=True)
    
    hourly_rate_cents = Column(Integer, nullable=True)
    project_rate_min_cents = Column(Integer, nullable=True)
    project_rate_max_cents = Column(Integer, nullable=True)
    retainer_rate_cents = Column(Integer, nullable=True)
    
    response_time = Column(String(100), nullable=True)
    
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    is_accepting_clients = Column(Boolean, default=True)
    max_active_clients = Column(Integer, default=5)
    current_active_clients = Column(Integer, default=0)
    
    projects_completed = Column(Integer, default=0)
    avg_rating = Column(Float, nullable=True)
    total_reviews = Column(Integer, default=0)
    response_rate = Column(Float, nullable=True)
    member_since = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
    expert = relationship("Expert", foreign_keys=[expert_id])


class ExpertEngagement(Base):
    """
    Tracks expert engagements with users.
    
    This extends the basic ExpertBooking model with workflow
    states, permission levels, and collaboration features.
    """
    
    __tablename__ = "expert_engagements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expert_profile_id = Column(Integer, ForeignKey("expert_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True, index=True)
    
    engagement_type = Column(Enum(EngagementType), nullable=False, default=EngagementType.CONSULTATION)
    status = Column(Enum(EngagementStatus), nullable=False, default=EngagementStatus.REQUEST_SENT)
    permission_level = Column(Enum(ExpertPermissionLevel), nullable=False, default=ExpertPermissionLevel.VIEWER)
    
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    scope_of_work = Column(Text, nullable=True)
    
    request_message = Column(Text, nullable=True)
    shared_materials = Column(Text, nullable=True)
    ai_pre_brief = Column(Text, nullable=True)
    
    proposal_message = Column(Text, nullable=True)
    proposed_scope = Column(Text, nullable=True)
    proposed_amount_cents = Column(Integer, nullable=True)
    proposed_duration_days = Column(Integer, nullable=True)
    proposed_milestones = Column(Text, nullable=True)
    
    final_amount_cents = Column(Integer, nullable=True)
    platform_fee_cents = Column(Integer, nullable=True)
    expert_payout_cents = Column(Integer, nullable=True)
    currency = Column(String(10), default="usd")
    
    for_consultation_duration_minutes = Column(Integer, nullable=True)
    for_project_duration_weeks = Column(Integer, nullable=True)
    for_retainer_months = Column(Integer, nullable=True)
    for_hourly_estimated_hours = Column(Numeric(6, 2), nullable=True)
    for_equity_percentage_bps = Column(Integer, nullable=True)
    
    preferred_start_date = Column(DateTime(timezone=True), nullable=True)
    actual_start_date = Column(DateTime(timezone=True), nullable=True)
    expected_end_date = Column(DateTime(timezone=True), nullable=True)
    actual_end_date = Column(DateTime(timezone=True), nullable=True)
    
    request_sent_at = Column(DateTime(timezone=True), nullable=True)
    proposal_sent_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    cancellation_reason = Column(Text, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_transfer_id = Column(String(255), nullable=True)
    escrow_status = Column(String(50), nullable=True)
    
    is_reviewed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
    expert_profile = relationship("ExpertProfile", foreign_keys=[expert_profile_id])
    workspace = relationship("UserWorkspace", foreign_keys=[workspace_id])
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id])
    cancelled_by_user = relationship("User", foreign_keys=[cancelled_by])
    
    messages = relationship("ExpertMessage", back_populates="engagement", cascade="all, delete-orphan")
    reviews = relationship("ExpertReview", back_populates="engagement", cascade="all, delete-orphan")
    milestones = relationship("EngagementMilestone", back_populates="engagement", cascade="all, delete-orphan")


class EngagementMilestone(Base):
    """
    Milestones for project-based engagements.
    
    Used for milestone-based payment releases from escrow.
    """
    
    __tablename__ = "engagement_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("expert_engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    order_index = Column(Integer, default=0)
    amount_cents = Column(Integer, nullable=True)
    percentage = Column(Numeric(5, 2), nullable=True)
    
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    deliverables = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    payment_released = Column(Boolean, default=False)
    payment_released_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    engagement = relationship("ExpertEngagement", back_populates="milestones")
    approved_by_user = relationship("User", foreign_keys=[approved_by])


class ExpertMessage(Base):
    """
    In-platform messaging between users and experts.
    """
    
    __tablename__ = "expert_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("expert_engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    
    attachments = Column(Text, nullable=True)
    
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    is_ai_suggestion = Column(Boolean, default=False)
    
    is_starred = Column(Boolean, default=False)
    
    reply_to_id = Column(Integer, ForeignKey("expert_messages.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    engagement = relationship("ExpertEngagement", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    reply_to = relationship("ExpertMessage", remote_side=[id])


class ExpertReview(Base):
    """
    Reviews and ratings for experts after engagement completion.
    """
    
    __tablename__ = "expert_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("expert_engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    expert_profile_id = Column(Integer, ForeignKey("expert_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    overall_rating = Column(Integer, nullable=False)
    expertise_rating = Column(Integer, nullable=True)
    communication_rating = Column(Integer, nullable=True)
    responsiveness_rating = Column(Integer, nullable=True)
    value_for_money_rating = Column(Integer, nullable=True)
    
    review_text = Column(Text, nullable=True)
    
    would_recommend = Column(Boolean, nullable=True)
    would_work_again = Column(Boolean, nullable=True)
    
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    
    expert_response = Column(Text, nullable=True)
    expert_responded_at = Column(DateTime(timezone=True), nullable=True)
    
    is_flagged = Column(Boolean, default=False)
    flagged_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    engagement = relationship("ExpertEngagement", back_populates="reviews")
    expert_profile = relationship("ExpertProfile")
    reviewer = relationship("User", foreign_keys=[reviewer_id])


class ExpertScheduledSession(Base):
    """
    Scheduled video/call sessions between users and experts.
    """
    
    __tablename__ = "expert_scheduled_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("expert_engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(500), nullable=True)
    agenda = Column(Text, nullable=True)
    
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    
    meeting_url = Column(String(1000), nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    ai_notes = Column(Text, nullable=True)
    ai_action_items = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    
    recording_url = Column(String(1000), nullable=True)
    transcript = Column(Text, nullable=True)
    
    is_cancelled = Column(Boolean, default=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    engagement = relationship("ExpertEngagement")
    cancelled_by_user = relationship("User", foreign_keys=[cancelled_by])
