"""
Saved Search Model

Represents saved search queries for the Opportunity Discovery Feed with alert notifications.
Supports email, push, and Slack notifications.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Search configuration
    name = Column(String(255), nullable=False)
    filters = Column(JSONB, nullable=False)  # Stores all filter parameters (category, feasibility, etc.)
    
    # Notification preferences (JSONB)
    # Structure: {"email": bool, "push": bool, "slack": bool, "frequency": "instant|daily"}
    notification_prefs = Column(JSONB, nullable=False, default=dict)
    
    # Alert tracking
    is_active = Column(Boolean, default=True, nullable=False)
    last_notified_at = Column(DateTime(timezone=True), nullable=True)
    match_count = Column(Integer, default=0, nullable=False)  # Total opportunities matched
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default="now()")
    updated_at = Column(DateTime(timezone=True), server_default="now()", onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="saved_searches")
