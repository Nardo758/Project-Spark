from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class DataSourceConfig(Base):
    """
    Admin-controlled configuration for inbound data sources (webhooks/scrapers).

    This intentionally duplicates some environment-based defaults so admins can:
    - enable/disable a source
    - set a per-source rate limit (per minute window)
    - manage per-source HMAC secrets (optional; falls back to env)
    """

    __tablename__ = "data_source_configs"

    source = Column(String(50), primary_key=True)  # e.g. "reddit", "google_maps"
    display_name = Column(String(120), nullable=True)

    is_enabled = Column(Boolean, nullable=False, server_default="true")
    rate_limit_per_minute = Column(Integer, nullable=False, server_default="100")

    # Optional per-source secret for signature verification (falls back to env)
    hmac_secret = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

