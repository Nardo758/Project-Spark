from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime
from app.db.database import Base


class RateLimitCounter(Base):
    """
    Rate limit counters for atomic rate limiting.
    Each row tracks request count per source per minute window.
    """
    __tablename__ = "rate_limit_counters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)
    window_start = Column(DateTime, nullable=False)
    count = Column(Integer, default=0, nullable=False)
    max_requests = Column(Integer, default=100, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_rate_limit_source_window', 'source', 'window_start', unique=True),
    )
