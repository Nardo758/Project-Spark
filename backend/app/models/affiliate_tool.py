"""Affiliate Tools model for tracking tool recommendations with affiliate links."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.db.database import Base


class AffiliateTool(Base):
    __tablename__ = "affiliate_tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    base_url = Column(String(500), nullable=False)
    affiliate_url = Column(String(1000), nullable=True)
    affiliate_code = Column(String(100), nullable=True)
    commission_rate = Column(Float, nullable=True)
    commission_type = Column(String(50), nullable=True)
    
    price_display = Column(String(100), nullable=True)
    best_for = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    
    click_count = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AffiliateClick(Base):
    __tablename__ = "affiliate_clicks"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    opportunity_id = Column(Integer, nullable=True, index=True)
    workspace_id = Column(Integer, nullable=True, index=True)
    
    source = Column(String(50), nullable=True)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    converted = Column(Boolean, default=False)
    conversion_value = Column(Float, nullable=True)
