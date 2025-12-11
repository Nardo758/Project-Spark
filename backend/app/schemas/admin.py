"""
Pydantic schemas for admin operations
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class AdminUserListItem(BaseModel):
    """User item in admin list"""
    id: int
    email: EmailStr
    name: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    is_banned: bool
    impact_points: int
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserDetail(BaseModel):
    """Detailed user info for admin"""
    id: int
    email: EmailStr
    name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    oauth_provider: Optional[str]
    impact_points: int
    badges: Optional[str]
    is_active: bool
    is_verified: bool
    is_admin: bool
    is_banned: bool
    ban_reason: Optional[str]
    otp_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]

    # Computed fields
    opportunity_count: int = 0
    validation_count: int = 0
    comment_count: int = 0

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    """Schema for admin updating user"""
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_banned: Optional[bool] = None
    ban_reason: Optional[str] = None


class AdminBanUser(BaseModel):
    """Schema for banning a user"""
    ban_reason: str


class AdminStats(BaseModel):
    """Admin dashboard statistics"""
    total_users: int
    active_users: int
    verified_users: int
    banned_users: int
    total_opportunities: int
    total_validations: int
    total_comments: int
    total_notifications: int


class AdminOpportunityListItem(BaseModel):
    """Opportunity item in admin list"""
    id: int
    title: str
    author_id: int
    author_name: str
    status: str
    validation_count: int
    comment_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class AdminActivityLog(BaseModel):
    """Activity log entry"""
    user_id: int
    user_name: str
    action: str
    resource_type: str
    resource_id: int
    timestamp: datetime
