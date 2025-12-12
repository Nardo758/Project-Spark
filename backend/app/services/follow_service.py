"""
Follow Service

Manages user following/followers relationships
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Tuple

from app.models.user import User
from app.models.follow import Follow
from app.services.notification import notification_service


class FollowService:
    """Service for managing user follows"""

    @staticmethod
    def follow_user(follower: User, following_id: int, db: Session) -> Tuple[bool, str]:
        """
        Follow a user

        Args:
            follower: User who is following
            following_id: ID of user to follow
            db: Database session

        Returns:
            (success, message)
        """
        # Can't follow yourself
        if follower.id == following_id:
            return False, "Cannot follow yourself"

        # Check if user exists
        following_user = db.query(User).filter(User.id == following_id).first()
        if not following_user:
            return False, "User not found"

        # Check if already following
        existing = db.query(Follow).filter(
            and_(
                Follow.follower_id == follower.id,
                Follow.following_id == following_id
            )
        ).first()

        if existing:
            return False, "Already following this user"

        # Create follow relationship
        follow = Follow(
            follower_id=follower.id,
            following_id=following_id
        )
        db.add(follow)
        db.commit()

        # Send notification
        notification_service.create_notification(
            db=db,
            user_id=following_id,
            notification_type="new_follower",
            title="New Follower",
            message=f"{follower.name} started following you",
            link=f"/users/{follower.id}",
            related_user_id=follower.id,
            send_email=False
        )

        return True, "Successfully followed user"

    @staticmethod
    def unfollow_user(follower: User, following_id: int, db: Session) -> Tuple[bool, str]:
        """
        Unfollow a user

        Args:
            follower: User who is unfollowing
            following_id: ID of user to unfollow
            db: Database session

        Returns:
            (success, message)
        """
        follow = db.query(Follow).filter(
            and_(
                Follow.follower_id == follower.id,
                Follow.following_id == following_id
            )
        ).first()

        if not follow:
            return False, "Not following this user"

        db.delete(follow)
        db.commit()

        return True, "Successfully unfollowed user"

    @staticmethod
    def is_following(follower_id: int, following_id: int, db: Session) -> bool:
        """Check if user is following another user"""
        follow = db.query(Follow).filter(
            and_(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id
            )
        ).first()

        return follow is not None

    @staticmethod
    def get_followers(user_id: int, skip: int, limit: int, db: Session) -> List[User]:
        """Get list of followers for a user"""
        followers = db.query(User).join(
            Follow,
            Follow.follower_id == User.id
        ).filter(
            Follow.following_id == user_id
        ).offset(skip).limit(limit).all()

        return followers

    @staticmethod
    def get_following(user_id: int, skip: int, limit: int, db: Session) -> List[User]:
        """Get list of users that a user is following"""
        following = db.query(User).join(
            Follow,
            Follow.following_id == User.id
        ).filter(
            Follow.follower_id == user_id
        ).offset(skip).limit(limit).all()

        return following

    @staticmethod
    def get_follower_count(user_id: int, db: Session) -> int:
        """Get count of followers for a user"""
        return db.query(Follow).filter(Follow.following_id == user_id).count()

    @staticmethod
    def get_following_count(user_id: int, db: Session) -> int:
        """Get count of users that a user is following"""
        return db.query(Follow).filter(Follow.follower_id == user_id).count()

    @staticmethod
    def get_mutual_followers(user1_id: int, user2_id: int, db: Session) -> List[User]:
        """Get users who follow both user1 and user2"""
        # Find followers of user1
        user1_followers = db.query(Follow.follower_id).filter(
            Follow.following_id == user1_id
        ).subquery()

        # Find followers of user2
        user2_followers = db.query(Follow.follower_id).filter(
            Follow.following_id == user2_id
        ).subquery()

        # Find intersection
        mutual = db.query(User).filter(
            User.id.in_(user1_followers),
            User.id.in_(user2_followers)
        ).all()

        return mutual


follow_service = FollowService()
