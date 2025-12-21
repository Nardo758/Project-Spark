from __future__ import annotations

import enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class LeadStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"
    EXPIRED = "expired"


class LeadPaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class LeadPaymentProvider(str, enum.Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    MANUAL = "manual"


class SavedSearchFrequency(str, enum.Enum):
    INSTANT = "instant"
    DAILY = "daily"
    WEEKLY = "weekly"


class MarketplaceLead(Base):
    """
    Leads Marketplace

    A MarketplaceLead is a purchasable, anonymized "package" derived from an Opportunity.
    """

    __tablename__ = "marketplace_leads"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=True, index=True)

    # User-facing identifier, e.g. "LD-12345"
    public_id = Column(String(32), nullable=False, unique=True, index=True)

    public_title = Column(String(255), nullable=False, index=True)
    anonymized_summary = Column(Text, nullable=False)

    industry = Column(String(120), nullable=True, index=True)
    deal_size_range = Column(String(80), nullable=True, index=True)
    location = Column(String(120), nullable=True, index=True)
    revenue_range = Column(String(80), nullable=True)

    status = Column(String(20), nullable=False, default=LeadStatus.DRAFT.value, index=True)
    lead_price_cents = Column(Integer, nullable=False, default=0)
    quality_score = Column(Integer, nullable=False, default=5)

    # Encrypted/secure storage in the future; for now JSON-in-Text.
    full_data_json = Column(Text, nullable=True)

    views_count = Column(Integer, nullable=False, default=0)
    purchase_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    admin_notes = Column(Text, nullable=True)

    opportunity = relationship("Opportunity")
    views = relationship("LeadView", back_populates="lead", cascade="all, delete-orphan")


class LeadView(Base):
    __tablename__ = "lead_views"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("marketplace_leads.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = Column(String(120), nullable=True)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("MarketplaceLead", back_populates="views")
    user = relationship("User")

