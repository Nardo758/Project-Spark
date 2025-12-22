from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class FeatureType(str, enum.Enum):
    point = "point"
    polygon = "polygon"
    linestring = "linestring"


class GeographicFeature(Base):
    __tablename__ = "geographic_features"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("scraped_sources.id"), nullable=True, index=True)
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    geojson = Column(JSONB, nullable=False)
    feature_type = Column(String(50), nullable=False, default="point")
    location_name = Column(String(500), nullable=True)
    city = Column(String(255), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    confidence_score = Column(Float, nullable=True)
    properties = Column(JSONB, nullable=True)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
