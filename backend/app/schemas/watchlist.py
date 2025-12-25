from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TagSchema(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


class OpportunityInWatchlist(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    market_size: Optional[str] = None
    ai_competition_level: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WatchlistItemCreate(BaseModel):
    """Schema for creating a watchlist item"""
    opportunity_id: int


class WatchlistItem(BaseModel):
    """Schema for watchlist item response"""
    id: int
    user_id: int
    opportunity_id: int
    collection_id: Optional[int] = None
    created_at: datetime
    opportunity: Optional[OpportunityInWatchlist] = None
    tags: List[TagSchema] = []

    class Config:
        from_attributes = True
