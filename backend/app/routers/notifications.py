"""
Notifications Router

Endpoints for managing user notifications
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import (
    Notification as NotificationSchema,
    NotificationMarkRead,
    NotificationStats
)
from app.core.dependencies import get_current_user
from app.services.notification import notification_service

router = APIRouter()


@router.get("/", response_model=List[NotificationSchema])
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notifications for current user

    Args:
        skip: Number of notifications to skip
        limit: Maximum number of notifications to return
        unread_only: Only return unread notifications
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    return notifications


@router.get("/stats", response_model=NotificationStats)
def get_notification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics for current user"""
    total = db.query(Notification).filter(Notification.user_id == current_user.id).count()
    unread = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {
        "total": total,
        "unread": unread
    }


@router.post("/mark-read")
def mark_notifications_read(
    request: NotificationMarkRead,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark specific notifications as read"""
    notification_service.mark_as_read(
        db=db,
        notification_ids=request.notification_ids,
        user_id=current_user.id
    )

    return {"message": "Notifications marked as read"}


@router.post("/mark-all-read")
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for current user"""
    notification_service.mark_all_as_read(db=db, user_id=current_user.id)

    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific notification"""
    deleted = notification_service.delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return {"message": "Notification deleted"}


@router.get("/{notification_id}", response_model=NotificationSchema)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # Mark as read when viewed
    if not notification.is_read:
        notification_service.mark_as_read(
            db=db,
            notification_ids=[notification_id],
            user_id=current_user.id
        )

    return notification
