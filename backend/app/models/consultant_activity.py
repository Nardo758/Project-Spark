from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ConsultantPath(str, enum.Enum):
    validate_idea = "validate_idea"
    search_ideas = "search_ideas"
    identify_location = "identify_location"


class ConsultantActivity(Base):
    __tablename__ = "consultant_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    path = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=True)
    result_summary = Column(Text, nullable=True)
    ai_model_used = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
