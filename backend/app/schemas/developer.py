from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    scopes: List[str] = Field(default_factory=list)


class ApiKeyOut(BaseModel):
    id: int
    name: str
    prefix: str
    is_active: bool
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApiKeyCreateResponse(BaseModel):
    api_key: str
    key: ApiKeyOut


class PublicApiOpportunity(BaseModel):
    id: int
    title: str
    description: str
    category: str
    market_size: Optional[str] = None
    growth_rate: float = 0.0
    feasibility_score: Optional[float] = None
    created_at: Optional[datetime] = None


class PublicApiOpportunityList(BaseModel):
    opportunities: List[PublicApiOpportunity]
    total: int
    page: int
    page_size: int

