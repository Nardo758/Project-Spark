"""
Partner Outreach Model

Tracks potential integration/tool partners and outreach status.
"""

from __future__ import annotations

import enum

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func

from app.db.database import Base


class PartnerOutreachStatus(str, enum.Enum):
    IDENTIFIED = "identified"
    CONTACTED = "contacted"
    IN_TALKS = "in_talks"
    ACTIVE = "active"
    PAUSED = "paused"
    REJECTED = "rejected"


class PartnerOutreach(Base):
    __tablename__ = "partner_outreach"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True)  # e.g. "payments", "crm", "analytics"
    website_url = Column(String(500), nullable=True)

    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)

    status = Column(Enum(PartnerOutreachStatus), nullable=False, default=PartnerOutreachStatus.IDENTIFIED)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

