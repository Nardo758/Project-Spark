"""
Pydantic schemas for subscriptions and billing
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionResponse(BaseModel):
    """User's subscription details"""
    tier: str
    status: str
    cancel_at_period_end: bool
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]

    class Config:
        from_attributes = True


class SubscriptionLimits(BaseModel):
    """Usage limits for subscription tier"""
    monthly_views: int
    monthly_unlocks: int
    export_limit: int
    export_batch_size: int
    api_access: bool
    price: int


class UsageStats(BaseModel):
    """Current usage statistics"""
    period_start: datetime
    period_end: datetime
    opportunity_views: int
    unlocked_opportunities: int
    csv_exports: int
    ideas_exported: int
    limits: SubscriptionLimits


class CheckoutSessionCreate(BaseModel):
    """Request to create checkout session"""
    tier: str  # 'pro' or 'business'
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Checkout session response"""
    session_id: str
    url: str


class PortalSessionResponse(BaseModel):
    """Customer portal session response"""
    url: str


class UnlockOpportunityRequest(BaseModel):
    """Request to unlock an opportunity"""
    opportunity_id: int


class UnlockOpportunityResponse(BaseModel):
    """Response after unlocking opportunity"""
    success: bool
    remaining_unlocks: int
    opportunity_id: int


class ExportRequest(BaseModel):
    """Request to export opportunities"""
    opportunity_ids: list[int]
    format: str = "csv"  # 'csv' or 'json'


class BillingInfo(BaseModel):
    """Billing information"""
    stripe_customer_id: Optional[str]
    has_payment_method: bool
    subscription: Optional[SubscriptionResponse]
    usage: Optional[UsageStats]
