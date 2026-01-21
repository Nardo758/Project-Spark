from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.validation import Validation
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas.user import User as UserSchema, UserUpdate, BadgeInfo
from app.core.dependencies import get_current_active_user
from app.services.badges import BadgeService

router = APIRouter()


def enrich_user_with_stats(user: User, db: Session) -> User:
    """Add computed stats to user object including subscription tier"""
    # Count validations
    validation_count = db.query(Validation).filter(Validation.user_id == user.id).count()
    user.validation_count = validation_count
    
    # Fetch fresh tier from subscriptions table
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if subscription and subscription.tier:
        tier_value = subscription.tier.value if hasattr(subscription.tier, 'value') else str(subscription.tier)
        user.tier = tier_value.lower()
    else:
        user.tier = "free"
    
    return user


@router.get("/me", response_model=UserSchema)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user profile with stats"""
    # Check and award any new badges
    BadgeService.check_and_award_badges(current_user, db)
    db.commit()

    # Enrich with stats
    return enrich_user_with_stats(current_user, db)


@router.put("/me", response_model=UserSchema)
def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user profile"""
    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return enrich_user_with_stats(current_user, db)


@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return enrich_user_with_stats(user, db)


@router.get("/me/badges/available", response_model=List[BadgeInfo])
def get_available_badges():
    """Get all available badges"""
    return BadgeService.get_all_badges()


@router.post("/me/badges/check")
def check_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check and award new badges for current user
    Returns list of newly awarded badges
    """
    newly_awarded = BadgeService.check_and_award_badges(current_user, db)
    db.commit()

    return {
        "newly_awarded": newly_awarded,
        "total_badges": len(BadgeService.get_user_badges(current_user))
    }
