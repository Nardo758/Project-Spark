from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from app.db.database import Base


class SuccessPattern(Base):
    """
    Transaction & Success DB (modeled as 'success_patterns').

    Captures outcomes + journey data so the AI Engine can learn.
    """

    __tablename__ = "success_patterns"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True, index=True)

    opportunity_type = Column(String(255), nullable=True)

    experts_used = Column(Text, nullable=True)  # JSON array[int]
    timeline = Column(Text, nullable=True)  # JSON

    capital_spent = Column(Numeric(14, 2), nullable=True)
    revenue_generated = Column(Numeric(14, 2), nullable=True)

    failure_points = Column(Text, nullable=True)  # JSON array[str]
    success_factors = Column(Text, nullable=True)  # JSON array[str]

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

