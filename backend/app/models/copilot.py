"""
Global AI Copilot models for cross-page conversation persistence.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class GlobalChatMessage(Base):
    """User-level chat messages for the persistent AI Copilot."""
    __tablename__ = "global_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    
    page_context = Column(String(100), nullable=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True)
    
    is_suggestion = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="copilot_messages")
    opportunity = relationship("Opportunity")

    __table_args__ = (
        Index('ix_global_chat_user_created', 'user_id', 'created_at'),
    )


class CopilotSuggestion(Base):
    """AI-generated proactive suggestions shown to users."""
    __tablename__ = "copilot_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    suggestion_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    
    page_context = Column(String(100), nullable=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True)
    
    is_dismissed = Column(Boolean, default=False)
    is_acted_on = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")
    opportunity = relationship("Opportunity")
