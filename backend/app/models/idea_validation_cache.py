from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base


class IdeaValidationCache(Base):
    __tablename__ = "idea_validation_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(64), nullable=False, unique=True, index=True)
    idea_description = Column(Text, nullable=False)
    business_context = Column(JSONB, nullable=True)
    
    recommendation = Column(String(50), nullable=True)
    online_score = Column(Float, nullable=True)
    physical_score = Column(Float, nullable=True)
    pattern_analysis = Column(JSONB, nullable=True)
    viability_report = Column(JSONB, nullable=True)
    similar_opportunities = Column(JSONB, nullable=True)
    
    processing_time_ms = Column(Integer, nullable=True)
    hit_count = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
