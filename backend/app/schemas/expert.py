from pydantic import BaseModel, Field
from typing import Optional, List, Any


class ExpertBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    headline: Optional[str] = None
    bio: Optional[str] = None
    website_url: Optional[str] = None
    skills: Optional[List[str]] = None
    specialization: Optional[List[str]] = None
    pricing_model: str = "hourly"
    hourly_rate_cents: Optional[int] = Field(default=None, ge=0)
    fixed_price_cents: Optional[int] = Field(default=None, ge=0)
    success_fee_bps: Optional[int] = Field(default=None, ge=0, le=10000)
    currency: str = "usd"
    availability: Optional[Any] = None
    is_active: bool = True


class ExpertCreate(ExpertBase):
    pass


class ExpertUpdate(BaseModel):
    name: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    website_url: Optional[str] = None
    skills: Optional[List[str]] = None
    specialization: Optional[List[str]] = None
    pricing_model: Optional[str] = None
    hourly_rate_cents: Optional[int] = Field(default=None, ge=0)
    fixed_price_cents: Optional[int] = Field(default=None, ge=0)
    success_fee_bps: Optional[int] = Field(default=None, ge=0, le=10000)
    currency: Optional[str] = None
    availability: Optional[Any] = None
    is_active: Optional[bool] = None


class ExpertResponse(ExpertBase):
    id: int

    class Config:
        from_attributes = True

