"""
Audit Log

Records security- and money-relevant actions for later review.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_type = Column(String(20), nullable=False, default="user")  # user|admin|system

    action = Column(String(120), nullable=False, index=True)
    resource_type = Column(String(80), nullable=True, index=True)
    resource_id = Column(String(80), nullable=True, index=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    metadata_json = Column(Text, nullable=True)  # JSON string

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

