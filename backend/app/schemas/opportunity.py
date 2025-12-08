from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
from app.models.opportunity import OpportunityStatus, OpportunitySource


class OpportunityBase(BaseModel):
    title: str
    description: str
    source: OpportunitySource
    source_url: str
    source_id: Optional[str] = None
    author: Optional[str] = None
    author_url: Optional[str] = None


class OpportunityScraperSubmit(OpportunityBase):
    """Schema for scrapers to submit opportunities"""
    category_slug: Optional[str] = None
    discovered_at: Optional[datetime] = None


class OpportunityCreate(OpportunityBase):
    category_id: Optional[int] = None


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[OpportunityStatus] = None
    friction_score: Optional[float] = None


class Opportunity(OpportunityBase):
    id: int
    category_id: Optional[int] = None
    friction_score: float
    validation_count: int
    agree_count: int
    disagree_count: int
    status: OpportunityStatus
    created_at: datetime
    updated_at: datetime
    discovered_at: Optional[datetime] = None

    class Config:
        from_attributes = True
