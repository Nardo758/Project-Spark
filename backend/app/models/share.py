from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class ShareEvent(Base):
    __tablename__ = "share_events"

    id = Column(Integer, primary_key=True, index=True)

    # What was shared
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)

    # Who shared it
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Where was it shared
    platform = Column(String(50), nullable=False)  # 'twitter', 'linkedin', 'facebook', 'email', 'copy_link'

    # Tracking
    share_url = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    opportunity = relationship("Opportunity")
    user = relationship("User")
