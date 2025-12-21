"""
Saved Search Model

Represents saved search queries for the Leads Marketplace with alert notifications.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    query = Column(String(500), nullable=True)
    filters = Column(JSON, nullable=True)
    
    alert_enabled = Column(Boolean, default=True, nullable=False)
    alert_frequency = Column(String(50), default="daily", nullable=False)
    last_alerted_at = Column(DateTime(timezone=True), nullable=True)
    
    match_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default="now()")
    updated_at = Column(DateTime(timezone=True), server_default="now()", onupdate=datetime.utcnow)

    user = relationship("User", backref="saved_searches")
