from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class DataSourceStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    error = "error"
    disabled = "disabled"


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default="active", nullable=False)
    
    base_weight = Column(Float, default=1.0)
    rate_limit_per_minute = Column(Integer, default=60)
    
    config = Column(JSONB, default=dict)
    location_extraction_config = Column(JSONB, default=dict)
    
    total_scrapes = Column(Integer, default=0)
    valid_opportunities = Column(Integer, default=0)
    failed_scrapes = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ValidationPattern(Base):
    __tablename__ = "validation_patterns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    regex_pattern = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    
    confidence = Column(Float, default=0.8)
    validation_level = Column(String(20), default="validated")
    
    source_specific = Column(JSONB, default=dict)
    
    hit_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)
    last_matched_at = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String(50), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    extra_data = Column(JSONB, default=dict)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=True, index=True)
    source_name = Column(String(100), nullable=False)
    job_type = Column(String(50), default="scheduled")
    
    status = Column(String(20), default="pending", index=True)
    priority = Column(Integer, default=5)
    
    config = Column(JSONB, default=dict)
    result = Column(JSONB, default=dict)
    
    items_processed = Column(Integer, default=0)
    items_accepted = Column(Integer, default=0)
    items_rejected = Column(Integer, default=0)
    
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
