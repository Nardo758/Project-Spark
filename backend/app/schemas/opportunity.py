from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OpportunityBase(BaseModel):
    title: str
    description: str
    category: str
    subcategory: Optional[str] = None
    severity: int
    market_size: Optional[str] = None
    is_anonymous: bool = False


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    severity: Optional[int] = None
    market_size: Optional[str] = None
    status: Optional[str] = None


class Opportunity(OpportunityBase):
    id: int
    validation_count: int = 0
    growth_rate: float = 0.0
    author_id: Optional[int] = None
    status: str = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OpportunityList(BaseModel):
    opportunities: list[Opportunity]
    total: int
    page: int
    page_size: int
