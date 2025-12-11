"""
Notification Service

Handles creating and managing notifications for users
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.notification import Notification
from app.models.user import User
from app.services.email import email_service


class NotificationService:
    """Service for managing notifications"""

    # Notification types
    TYPE_COMMENT = "comment"
    TYPE_VALIDATION = "validation"
    TYPE_BADGE_EARNED = "badge_earned"
    TYPE_OPPORTUNITY_COMPLETED = "opportunity_completed"
    TYPE_WATCHLIST_UPDATE = "watchlist_update"
    TYPE_SYSTEM = "system"

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        link: Optional[str] = None,
        related_user_id: Optional[int] = None,
        related_opportunity_id: Optional[int] = None,
        send_email: bool = False
    ) -> Notification:
        """
        Create a new notification

        Args:
            db: Database session
            user_id: ID of user to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            link: Optional link to related resource
            related_user_id: Optional ID of related user
            related_opportunity_id: Optional ID of related opportunity
            send_email: Whether to send email notification

        Returns:
            Created notification
        """
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            link=link,
            related_user_id=related_user_id,
            related_opportunity_id=related_opportunity_id,
            is_emailed=send_email
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Send email if requested
        if send_email:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                NotificationService.send_notification_email(
                    user=user,
                    notification=notification
                )

        return notification

    @staticmethod
    def send_notification_email(user: User, notification: Notification):
        """
        Send email notification to user

        Args:
            user: User to send email to
            notification: Notification to send
        """
        try:
            email_service.send_notification_email(
                to_email=user.email,
                user_name=user.name,
                notification_title=notification.title,
                notification_message=notification.message,
                notification_link=notification.link
            )
        except Exception as e:
            print(f"Failed to send notification email: {e}")

    @staticmethod
    def notify_new_comment(
        db: Session,
        opportunity_author_id: int,
        commenter_id: int,
        commenter_name: str,
        opportunity_id: int,
        opportunity_title: str
    ):
        """Notify opportunity author about new comment"""
        # Don't notify if user commented on their own post
        if opportunity_author_id == commenter_id:
            return

        NotificationService.create_notification(
            db=db,
            user_id=opportunity_author_id,
            notification_type=NotificationService.TYPE_COMMENT,
            title="New comment on your opportunity",
            message=f"{commenter_name} commented on \"{opportunity_title}\"",
            link=f"/opportunities/{opportunity_id}",
            related_user_id=commenter_id,
            related_opportunity_id=opportunity_id,
            send_email=True
        )

    @staticmethod
    def notify_new_validation(
        db: Session,
        opportunity_author_id: int,
        validator_id: int,
        validator_name: str,
        opportunity_id: int,
        opportunity_title: str,
        validation_type: str
    ):
        """Notify opportunity author about new validation"""
        # Don't notify if user validated their own post
        if opportunity_author_id == validator_id:
            return

        NotificationService.create_notification(
            db=db,
            user_id=opportunity_author_id,
            notification_type=NotificationService.TYPE_VALIDATION,
            title=f"New {validation_type} on your opportunity",
            message=f"{validator_name} marked \"{opportunity_title}\" as {validation_type}",
            link=f"/opportunities/{opportunity_id}",
            related_user_id=validator_id,
            related_opportunity_id=opportunity_id,
            send_email=True
        )

    @staticmethod
    def notify_badge_earned(
        db: Session,
        user_id: int,
        badge_name: str,
        badge_description: str
    ):
        """Notify user about earning a new badge"""
        NotificationService.create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationService.TYPE_BADGE_EARNED,
            title="Badge earned!",
            message=f"You earned the \"{badge_name}\" badge! {badge_description}",
            link="/profile",
            send_email=False  # Don't email for badges
        )

    @staticmethod
    def notify_opportunity_completed(
        db: Session,
        opportunity_author_id: int,
        opportunity_title: str,
        opportunity_id: int
    ):
        """Notify opportunity author when their opportunity is marked as completed"""
        NotificationService.create_notification(
            db=db,
            user_id=opportunity_author_id,
            notification_type=NotificationService.TYPE_OPPORTUNITY_COMPLETED,
            title="Opportunity marked as completed",
            message=f"Your opportunity \"{opportunity_title}\" has been marked as completed!",
            link=f"/opportunities/{opportunity_id}",
            related_opportunity_id=opportunity_id,
            send_email=True
        )

    @staticmethod
    def mark_as_read(db: Session, notification_ids: list[int], user_id: int):
        """
        Mark notifications as read

        Args:
            db: Database session
            notification_ids: List of notification IDs to mark as read
            user_id: User ID (for security check)
        """
        notifications = db.query(Notification).filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id
        ).all()

        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()

        db.commit()

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int):
        """Mark all notifications as read for a user"""
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).all()

        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()

        db.commit()

    @staticmethod
    def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
        """
        Delete a notification

        Args:
            db: Database session
            notification_id: ID of notification to delete
            user_id: User ID (for security check)

        Returns:
            True if deleted, False if not found
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if notification:
            db.delete(notification)
            db.commit()
            return True

        return False


notification_service = NotificationService()
