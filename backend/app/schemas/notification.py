"""
Pydantic schemas for notifications
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    """Base notification schema"""
    type: str
    title: str
    message: str
    link: Optional[str] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification"""
    user_id: int
    related_user_id: Optional[int] = None
    related_opportunity_id: Optional[int] = None


class Notification(NotificationBase):
    """Schema for notification response"""
    id: int
    user_id: int
    is_read: bool
    is_emailed: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    related_user_id: Optional[int] = None
    related_opportunity_id: Optional[int] = None

    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    """Schema for marking notifications as read"""
    notification_ids: list[int]


class NotificationStats(BaseModel):
    """Schema for notification statistics"""
    total: int
    unread: int
