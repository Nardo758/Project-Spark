from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.database import Base


class AICost(Base):
    """Track AI API costs for analytics and billing."""
    __tablename__ = "ai_costs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    
    provider = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    
    cost_usd = Column(Float, nullable=True)
    
    feature = Column(String(100), nullable=True, index=True)
    action = Column(String(100), nullable=True)
    
    request_metadata = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    latency_ms = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
