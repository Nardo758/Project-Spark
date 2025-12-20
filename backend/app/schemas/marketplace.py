from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MarketplaceLeadPublic(BaseModel):
    id: int
    public_id: str
    public_title: str
    anonymized_summary: str
    industry: Optional[str] = None
    deal_size_range: Optional[str] = None
    location: Optional[str] = None
    revenue_range: Optional[str] = None
    status: str
    lead_price_cents: int
    quality_score: int
    views_count: int
    purchase_count: int
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MarketplaceLeadDetail(MarketplaceLeadPublic):
    opportunity_id: Optional[int] = None
    full_data_json: Optional[str] = None
    has_purchased: bool = False


class MarketplaceLeadListResponse(BaseModel):
    leads: List[MarketplaceLeadPublic]
    total: int
    page: int
    page_size: int


class MarketplaceLeadCreateFromOpportunity(BaseModel):
    opportunity_id: int
    public_title: str
    anonymized_summary: str
    industry: Optional[str] = None
    deal_size_range: Optional[str] = None
    location: Optional[str] = None
    revenue_range: Optional[str] = None
    lead_price_cents: int = Field(..., ge=0)
    quality_score: int = Field(5, ge=1, le=10)
    full_data: Optional[Dict[str, Any]] = None


class MarketplaceSavedSearchCreate(BaseModel):
    name: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    notification_frequency: str = "instant"
    is_active: bool = True


class MarketplaceSavedSearch(BaseModel):
    id: int
    name: str
    filters: Dict[str, Any]
    notification_frequency: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MarketplacePurchase(BaseModel):
    id: int
    lead_id: int
    buyer_id: int
    payment_status: str
    payment_provider: Optional[str] = None
    amount_paid_cents: int
    purchased_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MarketplacePurchasesResponse(BaseModel):
    purchases: List[MarketplacePurchase]

