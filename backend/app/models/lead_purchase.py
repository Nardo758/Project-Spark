"""
Lead Purchase Model

Tracks purchases of leads by users in the Leads Marketplace.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base


class LeadPurchase(Base):
    __tablename__ = "lead_purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True)
    
    price_paid = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_charge_id = Column(String(255), nullable=True)
    
    status = Column(String(50), default="completed", nullable=False)
    
    purchased_at = Column(DateTime(timezone=True), server_default="now()")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    lead_snapshot = Column(String, nullable=True)

    user = relationship("User", backref="lead_purchases")
    lead = relationship("Lead", backref="purchases")
