from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Notification details
    type = Column(String(50), nullable=False)  # 'comment', 'validation', 'badge_earned', etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)  # Link to relevant resource

    # Metadata
    related_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    related_opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=True)

    # Status
    is_read = Column(Boolean, default=False)
    is_emailed = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    related_user = relationship("User", foreign_keys=[related_user_id])
