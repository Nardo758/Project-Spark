"""
Saved Search Pydantic Schemas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime


class NotificationPreferences(BaseModel):
    """Notification preferences structure"""
    email: bool = False
    push: bool = False
    slack: bool = False
    frequency: str = Field(default="daily", pattern="^(instant|daily)$")


class SavedSearchFilters(BaseModel):
    """Structure for saved search filters"""
    search: Optional[str] = None
    category: Optional[str] = None
    min_feasibility: Optional[int] = Field(None, ge=0, le=100)
    max_feasibility: Optional[int] = Field(None, ge=0, le=100)
    geographic_scope: Optional[str] = None
    country: Optional[str] = None
    completion_status: Optional[str] = None
    realm_type: Optional[str] = None
    min_validations: Optional[int] = Field(None, ge=0)
    max_age_days: Optional[int] = Field(None, ge=0)
    sort_by: str = "feasibility"


class SavedSearchCreate(BaseModel):
    """Schema for creating a saved search"""
    name: str = Field(..., min_length=1, max_length=255)
    filters: Dict[str, Any]  # Flexible filters
    notification_prefs: Dict[str, Any]  # Notification preferences
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class SavedSearchUpdate(BaseModel):
    """Schema for updating a saved search"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    filters: Optional[Dict[str, Any]] = None
    notification_prefs: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SavedSearchResponse(BaseModel):
    """Schema for saved search response"""
    id: int
    user_id: int
    name: str
    filters: Dict[str, Any]
    notification_prefs: Dict[str, Any]
    is_active: bool
    last_notified_at: Optional[datetime]
    match_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SavedSearchList(BaseModel):
    """Schema for list of saved searches"""
    saved_searches: list[SavedSearchResponse]
    total: int
