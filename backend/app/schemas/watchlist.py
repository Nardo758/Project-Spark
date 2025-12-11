from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.opportunity import Opportunity as OpportunitySchema


class WatchlistItemCreate(BaseModel):
    """Schema for creating a watchlist item"""
    opportunity_id: int


class WatchlistItem(BaseModel):
    """Schema for watchlist item response"""
    id: int
    user_id: int
    opportunity_id: int
    created_at: datetime
    opportunity: Optional[OpportunitySchema] = None

    class Config:
        from_attributes = True
