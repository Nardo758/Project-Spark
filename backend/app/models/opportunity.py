from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class OpportunityStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class OpportunitySource(str, enum.Enum):
    reddit = "reddit"
    twitter = "twitter"
    linkedin = "linkedin"
    github = "github"
    hackernews = "hackernews"
    producthunt = "producthunt"
    other = "other"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    source = Column(Enum(OpportunitySource), nullable=False)
    source_url = Column(String, nullable=False)
    source_id = Column(String, index=True)  # Original ID from source platform
    author = Column(String)
    author_url = Column(String)

    # Category
    category_id = Column(Integer, ForeignKey("categories.id"))

    # Metrics
    friction_score = Column(Float, default=0.0)  # 0-100 score
    validation_count = Column(Integer, default=0)
    agree_count = Column(Integer, default=0)
    disagree_count = Column(Integer, default=0)

    # Status
    status = Column(Enum(OpportunityStatus), default=OpportunityStatus.pending)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    discovered_at = Column(DateTime)  # When scraper found it

    # Relationships
    category = relationship("Category", back_populates="opportunities")
    validations = relationship("Validation", back_populates="opportunity")
