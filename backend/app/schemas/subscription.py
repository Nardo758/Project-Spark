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


class PortalSessionCreate(BaseModel):
    """Request to create customer portal session"""
    return_url: str


class PortalSessionResponse(BaseModel):
    """Customer portal session response"""
    url: str


class SubscriptionIntentCreate(BaseModel):
    """Request to create an in-app subscription payment intent (Elements modal)."""
    tier: str  # 'pro' or 'business'


class SubscriptionIntentResponse(BaseModel):
    """Response with PaymentIntent client secret for subscription signup."""
    stripe_subscription_id: str
    client_secret: str


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


class PayPerUnlockRequest(BaseModel):
    """Request to create pay-per-unlock payment"""
    opportunity_id: int


class PayPerUnlockResponse(BaseModel):
    """Response with payment intent for pay-per-unlock"""
    client_secret: str
    payment_intent_id: str
    amount: int  # In cents
    opportunity_id: int


class OpportunityAccessInfo(BaseModel):
    """Access info for an opportunity based on user's tier"""
    opportunity_id: int
    age_days: int
    freshness_badge: dict
    is_accessible: bool
    is_unlocked: bool
    unlock_method: Optional[str]
    days_until_unlock: int
    can_pay_to_unlock: bool
    unlock_price: Optional[int]  # In cents, if pay-per-unlock available
