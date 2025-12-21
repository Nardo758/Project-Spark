from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class BusinessType(str, enum.Enum):
    specific_business = "specific_business"
    retail = "retail"
    multifamily = "multifamily"
    hospitality = "hospitality"


class LocationAnalysisCache(Base):
    __tablename__ = "location_analysis_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), nullable=False, unique=True, index=True)
    city = Column(String(255), nullable=False, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    business_type = Column(String(50), nullable=False, index=True)
    business_subtype = Column(String(100), nullable=True)
    query_params = Column(JSONB, nullable=True)
    geojson_snapshot = Column(JSONB, nullable=True)
    demographic_data = Column(JSONB, nullable=True)
    market_metrics = Column(JSONB, nullable=True)
    claude_summary = Column(Text, nullable=True)
    site_recommendations = Column(JSONB, nullable=True)
    hit_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
