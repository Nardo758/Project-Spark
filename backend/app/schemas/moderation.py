"""
Pydantic schemas for content moderation
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReportCreate(BaseModel):
    """Schema for creating a report"""
    content_type: str  # 'opportunity', 'comment', 'user'
    content_id: int
    reason: str  # 'spam', 'harassment', 'inappropriate', etc.
    description: Optional[str] = None


class ReportResponse(BaseModel):
    """Schema for report response"""
    id: int
    reporter_id: int
    content_type: str
    content_id: int
    reason: str
    description: Optional[str]
    status: str
    moderator_id: Optional[int]
    moderator_notes: Optional[str]
    action_taken: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReportResolve(BaseModel):
    """Schema for resolving a report"""
    action_taken: str  # 'deleted', 'warned', 'dismissed', 'banned'
    moderator_notes: Optional[str] = None


class ReportDismiss(BaseModel):
    """Schema for dismissing a report"""
    moderator_notes: Optional[str] = None


class ModerationStats(BaseModel):
    """Schema for moderation statistics"""
    pending_reports: int
    reviewing_reports: int
    resolved_reports_today: int
    total_reports: int
    top_reported_content: List[dict]


class ModerationLogResponse(BaseModel):
    """Schema for moderation log"""
    id: int
    moderator_id: Optional[int]
    action: str
    content_type: str
    content_id: int
    reason: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ContentModerationResult(BaseModel):
    """Schema for automated moderation result"""
    is_safe: bool
    warnings: List[str]
    flags: List[dict]
