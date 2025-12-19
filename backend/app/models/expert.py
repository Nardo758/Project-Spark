from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Numeric, Boolean
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ExpertPricingModel(str, enum.Enum):
    HOURLY = "hourly"
    FIXED = "fixed"
    PACKAGE = "package"
    SUCCESS_FEE = "success_fee"


class Expert(Base):
    """
    Expert/Service DB.

    This is the catalog used by the Expert API Gateway / Marketplace layer.
    """

    __tablename__ = "experts"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, index=True)
    headline = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    website_url = Column(String(1000), nullable=True)

    # Skills / specialization (JSON-in-Text for portability)
    skills = Column(Text, nullable=True)  # JSON array[str]
    specialization = Column(Text, nullable=True)  # JSON array[str]

    # Performance
    success_rate = Column(Numeric(5, 2), nullable=True)  # percent
    avg_delivery_time_days = Column(Integer, nullable=True)
    ratings = Column(Text, nullable=True)  # JSON array
    ai_match_score = Column(Numeric(6, 3), nullable=True)

    # Pricing
    pricing_model = Column(Enum(ExpertPricingModel), nullable=False, default=ExpertPricingModel.HOURLY)
    hourly_rate_cents = Column(Integer, nullable=True)
    fixed_price_cents = Column(Integer, nullable=True)
    success_fee_bps = Column(Integer, nullable=True)  # basis points (e.g. 500 = 5.00%)
    currency = Column(String(10), default="usd")

    # Availability and status
    availability = Column(Text, nullable=True)  # JSON
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

