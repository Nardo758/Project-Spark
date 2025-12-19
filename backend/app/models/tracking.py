"""
Tracking / Analytics Events

Lightweight event capture for product analytics and funnel debugging.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.db.database import Base


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, index=True)  # e.g. "page_view", "cta_click"
    path = Column(String(500), nullable=True, index=True)
    referrer = Column(String(500), nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    anonymous_id = Column(String(64), nullable=True, index=True)

    properties = Column(Text, nullable=True)  # JSON string

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

