"""
Pydantic schemas for admin operations
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from pydantic import Field


class AdminUserListItem(BaseModel):
    """User item in admin list"""
    id: int
    email: EmailStr
    name: str
    is_active: bool = False
    is_verified: bool = False
    is_admin: bool = False
    is_banned: bool = False
    impact_points: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserDetail(BaseModel):
    """Detailed user info for admin"""
    id: int
    email: EmailStr
    name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    oauth_provider: Optional[str] = None
    impact_points: int = 0
    badges: Optional[str] = None
    is_active: bool = False
    is_verified: bool = False
    is_admin: bool = False
    is_banned: bool = False
    ban_reason: Optional[str] = None
    otp_enabled: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

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


class AdminStripeWebhookEvent(BaseModel):
    """Stripe webhook event processing record (idempotency + status)."""
    stripe_event_id: str
    event_type: str
    livemode: bool
    status: str
    attempt_count: int
    stripe_created_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminStripeWebhookEventList(BaseModel):
    items: List[AdminStripeWebhookEvent]
    total: int


class AdminPayPerUnlockAttempt(BaseModel):
    """Pay-per-unlock attempt record (prevents concurrency limit bypass)."""
    id: int
    user_id: int
    opportunity_id: int
    attempt_date: date
    status: str
    stripe_payment_intent_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminPayPerUnlockAttemptList(BaseModel):
    items: List[AdminPayPerUnlockAttempt]
    total: int


class AdminIdeaValidation(BaseModel):
    """Persisted Idea Validation record (admin visibility)."""

    id: int
    user_id: int
    title: str
    category: str
    status: str

    stripe_payment_intent_id: Optional[str] = None
    amount_cents: Optional[int] = None
    currency: Optional[str] = None

    opportunity_score: Optional[int] = None
    validation_confidence: Optional[int] = None
    summary: Optional[str] = None
    # Included only when requested (see /admin/idea-validations?include_result=true)
    result_json: Optional[str] = None
    error_message: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminIdeaValidationList(BaseModel):
    items: List[AdminIdeaValidation]
    total: int


class AdminPartnerOutreachBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = None
    website_url: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AdminPartnerOutreachCreate(AdminPartnerOutreachBase):
    name: str


class AdminPartnerOutreachUpdate(AdminPartnerOutreachBase):
    pass


class AdminPartnerOutreach(AdminPartnerOutreachBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

