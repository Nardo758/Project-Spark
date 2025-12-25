from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class LocationType(str, enum.Enum):
    city = "city"
    neighborhood = "neighborhood"
    zip_code = "zip_code"
    business_district = "business_district"
    custom = "custom"


class MatchType(str, enum.Enum):
    exact = "exact"
    phrase = "phrase"
    broad = "broad"


class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ScheduleType(str, enum.Enum):
    once = "once"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class LocationCatalog(Base):
    __tablename__ = "location_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    normalized_name = Column(String(200), nullable=False, index=True)
    place_id = Column(String(255), unique=True, nullable=True)
    location_type = Column(String(50), default="city")
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_km = Column(Float, default=5.0)
    
    bounds_ne_lat = Column(Float, nullable=True)
    bounds_ne_lng = Column(Float, nullable=True)
    bounds_sw_lat = Column(Float, nullable=True)
    bounds_sw_lng = Column(Float, nullable=True)
    
    parent_location_id = Column(Integer, ForeignKey("location_catalog.id"), nullable=True)
    population = Column(Integer, nullable=True)
    business_count = Column(Integer, nullable=True)
    
    google_maps_url = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    extra_data = Column(JSONB, default=dict)
    
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    scraped_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    children = relationship("LocationCatalog", backref="parent", remote_side=[id])
    jobs = relationship("GoogleScrapeJob", back_populates="location")


class KeywordGroup(Base):
    __tablename__ = "keyword_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    keywords = Column(ARRAY(Text), nullable=False)
    description = Column(Text, nullable=True)
    
    match_type = Column(String(20), default="phrase")
    negative_keywords = Column(ARRAY(Text), default=list)
    required_patterns = Column(ARRAY(Text), default=list)
    language = Column(String(10), default="en")
    
    total_searches = Column(Integer, default=0)
    hit_rate = Column(Float, default=0.0)
    avg_opportunities_per_search = Column(Float, default=0.0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    jobs = relationship("GoogleScrapeJob", back_populates="keyword_group")


class GoogleScrapeJob(Base):
    __tablename__ = "google_scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("location_catalog.id"), nullable=True)
    keyword_group_id = Column(Integer, ForeignKey("keyword_groups.id"), nullable=True)
    name = Column(String(200), nullable=False)
    
    source_type = Column(String(50), nullable=False)
    depth = Column(Integer, default=50)
    radius_km = Column(Integer, default=5)
    language = Column(String(10), default="en-US")
    sort_by = Column(String(50), default="relevance")
    min_rating = Column(Integer, default=1)
    max_age_days = Column(Integer, nullable=True)
    
    schedule_type = Column(String(20), default="once")
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String(20), default="pending", index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    progress_current = Column(Integer, default=0)
    progress_total = Column(Integer, default=0)
    
    total_found = Column(Integer, default=0)
    total_processed = Column(Integer, default=0)
    opportunities_found = Column(Integer, default=0)
    last_result_at = Column(DateTime(timezone=True), nullable=True)
    
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    results = Column(JSONB, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    location = relationship("LocationCatalog", back_populates="jobs")
    keyword_group = relationship("KeywordGroup", back_populates="jobs")


class GoogleMapsBusiness(Base):
    __tablename__ = "google_maps_businesses"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(500), nullable=False)
    address = Column(Text, nullable=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_id = Column(Integer, ForeignKey("location_catalog.id"), nullable=True)
    
    types = Column(ARRAY(Text), default=list)
    rating = Column(Float, nullable=True)
    user_ratings_total = Column(Integer, nullable=True)
    price_level = Column(Integer, nullable=True)
    website = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    scraped_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GoogleSearchCache(Base):
    __tablename__ = "google_search_cache"

    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    location_query = Column(Text, nullable=False)
    keyword_query = Column(Text, nullable=False)
    search_type = Column(String(50), nullable=True)
    
    total_results = Column(Integer, nullable=True)
    search_time_ms = Column(Integer, nullable=True)
    detected_location = Column(Text, nullable=True)
    language = Column(String(10), nullable=True)
    
    raw_results = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
