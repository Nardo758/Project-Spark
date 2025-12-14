from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)

    # Categorization
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True)

    # Metrics
    severity = Column(Integer, nullable=False)  # 1-5 scale
    validation_count = Column(Integer, default=0)
    growth_rate = Column(Float, default=0.0)  # Week-over-week percentage
    market_size = Column(String(50), nullable=True)  # e.g., "$10M-$100M"

    # Geographic Information
    geographic_scope = Column(String(50), default="online")  # local, regional, national, international, online
    country = Column(String(100), nullable=True)  # Country name or code
    region = Column(String(100), nullable=True)  # State/Province/Region
    city = Column(String(100), nullable=True)  # City name

    # Completion Tracking
    completion_status = Column(String(50), default="open")  # open, in_progress, solved, abandoned
    solution_description = Column(Text, nullable=True)  # Description of solution if solved
    solved_at = Column(DateTime(timezone=True), nullable=True)  # When was it solved
    solved_by = Column(String(255), nullable=True)  # Company/person who solved it

    # Feasibility Metrics
    feasibility_score = Column(Float, nullable=True)  # Calculated feasibility score (0-100)
    duplicate_of = Column(Integer, ForeignKey("opportunities.id"), nullable=True)  # Link to original if duplicate

    # Author
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_anonymous = Column(Boolean, default=False)

    # Status
    status = Column(String(50), default="active")  # active, resolved, archived

    # Source Tracking (for scraped data)
    source_id = Column(String(255), nullable=True, unique=True, index=True)  # External ID from source
    source_url = Column(String(1000), nullable=True)  # Original URL
    source_platform = Column(String(50), nullable=True)  # reddit, twitter, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="opportunities")
    validations = relationship("Validation", back_populates="opportunity", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="opportunity", cascade="all, delete-orphan")
