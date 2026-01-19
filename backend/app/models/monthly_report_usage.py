"""
Monthly Report Usage Model
Tracks how many free reports a user has consumed each month
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class MonthlyReportUsage(Base):
    __tablename__ = "monthly_report_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    year_month = Column(String(7), nullable=False)
    
    reports_used = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="monthly_report_usage")

    __table_args__ = (
        UniqueConstraint("user_id", "year_month", name="uq_user_year_month"),
    )
