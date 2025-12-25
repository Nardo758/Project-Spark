import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class ReportType(str, enum.Enum):
    FEASIBILITY_STUDY = "feasibility_study"
    MARKET_ANALYSIS = "market_analysis"
    STRATEGIC_ASSESSMENT = "strategic_assessment"
    PROGRESS_REPORT = "progress_report"
    LAYER_1_OVERVIEW = "layer_1_overview"
    LAYER_2_DEEP_DIVE = "layer_2_deep_dive"
    LAYER_3_EXECUTION = "layer_3_execution"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True, index=True)
    
    report_type = Column(Enum(ReportType), nullable=False, index=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    
    confidence_score = Column(Integer, nullable=True)
    
    generation_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="generated_reports")
    opportunity = relationship("Opportunity", back_populates="generated_reports")
