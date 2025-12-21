"""
Lead Schemas

Pydantic schemas for Lead CRUD operations.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LeadCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = "organic"
    interest_category: Optional[str] = None
    notes: Optional[str] = None
    opportunity_id: Optional[int] = None
    email_opt_in: Optional[bool] = True


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    interest_category: Optional[str] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None
    email_opt_in: Optional[bool] = None


class LeadResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    company: Optional[str]
    phone: Optional[str]
    status: str
    source: str
    interest_category: Optional[str]
    notes: Optional[str]
    user_id: Optional[int]
    assigned_to_id: Optional[int]
    opportunity_id: Optional[int]
    last_contacted_at: Optional[datetime]
    converted_at: Optional[datetime]
    email_opt_in: bool
    email_sequence_step: int
    last_email_sent_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int


class LeadStats(BaseModel):
    total: int
    new: int
    contacted: int
    qualified: int
    nurturing: int
    converted: int
    lost: int
    conversion_rate: float
