"""
Follows Router

Endpoints for user following/followers system
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.services.follow_service import follow_service

router = APIRouter()


class FollowRequest(BaseModel):
    """Request to follow a user"""
    user_id: int


class FollowStats(BaseModel):
    """Follow statistics"""
    followers_count: int
    following_count: int
    is_following: bool  # If current user is following this user


class UserListItem(BaseModel):
    """User item in follower/following list"""
    id: int
    name: str
    email: str
    avatar_url: str = None
    impact_points: int = 0

    class Config:
        from_attributes = True


@router.post("/follow")
def follow_user(
    follow_data: FollowRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    success, message = follow_service.follow_user(
        follower=current_user,
        following_id=follow_data.user_id,
        db=db
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    return {"message": message}


@router.post("/unfollow")
def unfollow_user(
    follow_data: FollowRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    success, message = follow_service.unfollow_user(
        follower=current_user,
        following_id=follow_data.user_id,
        db=db
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    return {"message": message}


@router.get("/{user_id}/stats", response_model=FollowStats)
def get_follow_stats(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get follow statistics for a user"""
    followers_count = follow_service.get_follower_count(user_id, db)
    following_count = follow_service.get_following_count(user_id, db)
    is_following = follow_service.is_following(current_user.id, user_id, db)

    return {
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following
    }


@router.get("/{user_id}/followers", response_model=List[UserListItem])
def get_followers(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of followers for a user"""
    followers = follow_service.get_followers(user_id, skip, limit, db)
    return followers


@router.get("/{user_id}/following", response_model=List[UserListItem])
def get_following(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of users that a user is following"""
    following = follow_service.get_following(user_id, skip, limit, db)
    return following


@router.get("/check/{user_id}")
def check_following(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if current user is following another user"""
    is_following = follow_service.is_following(current_user.id, user_id, db)
    return {"is_following": is_following}


@router.get("/mutual/{user_id}", response_model=List[UserListItem])
def get_mutual_followers(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mutual followers between current user and another user"""
    mutual = follow_service.get_mutual_followers(current_user.id, user_id, db)
    return mutual


@router.get("/suggested")
def get_suggested_users(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get suggested users to follow based on impact points"""
    # Get users current user is NOT following
    following_ids = [u.id for u in follow_service.get_following(current_user.id, 0, 1000, db)]
    following_ids.append(current_user.id)  # Exclude self

    suggested = db.query(User).filter(
        User.id.notin_(following_ids),
        User.is_active == True
    ).order_by(User.impact_points.desc()).limit(limit).all()

    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "avatar_url": u.avatar_url,
            "impact_points": u.impact_points,
            "followers_count": follow_service.get_follower_count(u.id, db)
        }
        for u in suggested
    ]
