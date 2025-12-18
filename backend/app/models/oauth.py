from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class OAuthToken(Base):
    """
    Database-backed OAuth token storage for Replit Auth.
    Stores access tokens, refresh tokens, and session data per user/browser session.
    """
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    browser_session_key = Column(String(64), nullable=False, index=True)
    provider = Column(String(50), nullable=False, default="replit")
    
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), nullable=True, default="Bearer")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="oauth_tokens")

    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'browser_session_key',
            'provider',
            name='uq_user_browser_session_provider'
        ),
    )
