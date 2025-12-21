from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func
from app.db.database import Base


class DetectedTrend(Base):
    __tablename__ = "detected_trends"

    id = Column(Integer, primary_key=True, index=True)
    trend_name = Column(String(255), nullable=False, index=True)
    trend_strength = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    category = Column(String(100), nullable=True, index=True)
    source_type = Column(String(50), nullable=True)
    opportunities_count = Column(Integer, nullable=False, default=0)
    growth_rate = Column(Float, nullable=True)
    confidence_score = Column(Integer, nullable=True)
    ai_signature = Column(JSONB, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
