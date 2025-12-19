"""
Background Job Runs

Durable log of scheduled/background job executions for monitoring and retries.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.db.database import Base


class JobRun(Base):
    __tablename__ = "job_runs"

    id = Column(Integer, primary_key=True, index=True)

    job_name = Column(String(120), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)  # running|succeeded|failed

    started_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    details_json = Column(Text, nullable=True)
    error = Column(Text, nullable=True)

