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

    # Author
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_anonymous = Column(Boolean, default=False)

    # Status
    status = Column(String(50), default="active")  # active, resolved, archived

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="opportunities")
    validations = relationship("Validation", back_populates="opportunity", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="opportunity", cascade="all, delete-orphan")
