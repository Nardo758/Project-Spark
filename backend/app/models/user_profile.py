from sqlalchemy import Column, Integer, ForeignKey, Text, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from app.db.database import Base
import enum


class ExperienceLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LearningStyle(str, enum.Enum):
    READING = "reading"
    VIDEOS = "videos"
    HANDS_ON = "hands_on"
    COACHING = "coaching"


class UserProfile(Base):
    """
    User Intelligence DB (modeled as a dedicated table).

    Stored as JSON-in-Text fields for portability across DBs (Postgres/SQLite).
    """

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Profile intelligence
    skills = Column(Text, nullable=True)  # JSON array of strings
    experience_level = Column(Enum(ExperienceLevel), nullable=True)
    risk_tolerance = Column(Integer, nullable=True)  # 0-100
    available_capital = Column(Numeric(12, 2), nullable=True)
    time_commitment_hours_per_week = Column(Integer, nullable=True)
    past_successes = Column(Text, nullable=True)  # JSON
    failure_patterns = Column(Text, nullable=True)  # JSON
    learning_style = Column(Enum(LearningStyle), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="profile")

