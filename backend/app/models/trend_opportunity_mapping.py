from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base


class TrendOpportunityMapping(Base):
    __tablename__ = "trend_opportunity_mapping"

    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(Integer, ForeignKey("detected_trends.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    relevance_score = Column(Float, nullable=False, default=0.0)
    relationship_metadata = Column(JSONB, nullable=True)
    mapped_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('trend_id', 'opportunity_id', name='uq_trend_opportunity'),
    )
