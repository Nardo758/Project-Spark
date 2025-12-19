"""
Admin Router

Administrative endpoints for managing users, content, and platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date

from app.db.database import get_db
from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.validation import Validation
from app.models.comment import Comment
from app.models.notification import Notification
from app.schemas.admin import (
    AdminUserListItem,
    AdminUserDetail,
    AdminUserUpdate,
    AdminBanUser,
    AdminStats,
    AdminOpportunityListItem,
    AdminStripeWebhookEventList,
    AdminPayPerUnlockAttemptList,
)
from app.core.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/stats", response_model=AdminStats)
def get_admin_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get platform statistics for admin dashboard"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    banned_users = db.query(User).filter(User.is_banned == True).count()

    total_opportunities = db.query(Opportunity).count()
    total_validations = db.query(Validation).count()
    total_comments = db.query(Comment).count()
    total_notifications = db.query(Notification).count()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "banned_users": banned_users,
        "total_opportunities": total_opportunities,
        "total_validations": total_validations,
        "total_comments": total_comments,
        "total_notifications": total_notifications
    }


@router.get("/stripe/webhook-events", response_model=AdminStripeWebhookEventList)
def list_stripe_webhook_events(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None, description="processing|processed|failed"),
    event_type: Optional[str] = Query(None),
    livemode: Optional[bool] = Query(None),
    search_event_id: Optional[str] = Query(None, description="Substring match on evt_* id"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List recent Stripe webhook events for debugging and reliability monitoring."""
    from app.models.stripe_event import StripeWebhookEvent, StripeWebhookEventStatus

    q = db.query(StripeWebhookEvent)

    if status_filter:
        try:
            q = q.filter(StripeWebhookEvent.status == StripeWebhookEventStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status_filter")

    if event_type:
        q = q.filter(StripeWebhookEvent.event_type == event_type)

    if livemode is not None:
        q = q.filter(StripeWebhookEvent.livemode == livemode)

    if search_event_id:
        q = q.filter(StripeWebhookEvent.stripe_event_id.ilike(f"%{search_event_id}%"))

    total = q.count()
    items = q.order_by(desc(StripeWebhookEvent.received_at)).offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.get("/stripe/pay-per-unlock-attempts", response_model=AdminPayPerUnlockAttemptList)
def list_pay_per_unlock_attempts(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    user_id: Optional[int] = Query(None),
    opportunity_id: Optional[int] = Query(None),
    attempt_date: Optional[date] = Query(None),
    status_filter: Optional[str] = Query(None, description="created|succeeded|failed|canceled"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List pay-per-unlock attempts (includes pre-payment attempts to detect spam/race)."""
    from app.models.stripe_event import PayPerUnlockAttempt, PayPerUnlockAttemptStatus

    q = db.query(PayPerUnlockAttempt)

    if user_id is not None:
        q = q.filter(PayPerUnlockAttempt.user_id == user_id)
    if opportunity_id is not None:
        q = q.filter(PayPerUnlockAttempt.opportunity_id == opportunity_id)
    if attempt_date is not None:
        q = q.filter(PayPerUnlockAttempt.attempt_date == attempt_date)

    if status_filter:
        try:
            q = q.filter(PayPerUnlockAttempt.status == PayPerUnlockAttemptStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status_filter")

    total = q.count()
    items = q.order_by(desc(PayPerUnlockAttempt.created_at)).offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.get("/users", response_model=List[AdminUserListItem])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_banned: Optional[bool] = Query(None),
    is_admin: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List users with filtering and search"""
    query = db.query(User)

    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_pattern)) |
            (User.name.ilike(search_pattern))
        )

    if is_banned is not None:
        query = query.filter(User.is_banned == is_banned)

    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)

    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)

    # Order by created_at desc and paginate
    users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()

    return users


@router.get("/users/{user_id}", response_model=AdminUserDetail)
def get_user_detail(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed user information"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get counts
    opportunity_count = db.query(Opportunity).filter(Opportunity.author_id == user_id).count()
    validation_count = db.query(Validation).filter(Validation.user_id == user_id).count()
    comment_count = db.query(Comment).filter(Comment.user_id == user_id).count()

    # Add computed fields
    user_dict = {
        **user.__dict__,
        "opportunity_count": opportunity_count,
        "validation_count": validation_count,
        "comment_count": comment_count
    }

    return user_dict


@router.patch("/users/{user_id}", response_model=AdminUserDetail)
def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user settings (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admins from removing their own admin status
    if user_id == admin_user.id and user_update.is_admin is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own admin status"
        )

    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    # Get counts for response
    opportunity_count = db.query(Opportunity).filter(Opportunity.author_id == user_id).count()
    validation_count = db.query(Validation).filter(Validation.user_id == user_id).count()
    comment_count = db.query(Comment).filter(Comment.user_id == user_id).count()

    user_dict = {
        **user.__dict__,
        "opportunity_count": opportunity_count,
        "validation_count": validation_count,
        "comment_count": comment_count
    }

    return user_dict


@router.post("/users/{user_id}/ban")
def ban_user(
    user_id: int,
    ban_data: AdminBanUser,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Ban a user"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admins from banning themselves
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot ban yourself"
        )

    # Prevent banning other admins
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot ban admin users"
        )

    user.is_banned = True
    user.ban_reason = ban_data.ban_reason
    user.is_active = False
    db.commit()

    return {"message": "User banned successfully"}


@router.post("/users/{user_id}/unban")
def unban_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Unban a user"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_banned = False
    user.ban_reason = None
    user.is_active = True
    db.commit()

    return {"message": "User unbanned successfully"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user (dangerous operation)"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admins from deleting themselves
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    # Prevent deleting other admins
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin users"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


@router.get("/opportunities", response_model=List[AdminOpportunityListItem])
def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List opportunities with filtering"""
    query = db.query(
        Opportunity.id,
        Opportunity.title,
        Opportunity.author_id,
        User.name.label("author_name"),
        Opportunity.status,
        Opportunity.validation_count,
        Opportunity.comment_count,
        Opportunity.created_at
    ).join(User, Opportunity.author_id == User.id)

    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(Opportunity.title.ilike(search_pattern))

    if status_filter:
        query = query.filter(Opportunity.status == status_filter)

    # Order by created_at desc and paginate
    opportunities = query.order_by(desc(Opportunity.created_at)).offset(skip).limit(limit).all()

    return [
        {
            "id": opp.id,
            "title": opp.title,
            "author_id": opp.author_id,
            "author_name": opp.author_name,
            "status": opp.status,
            "validation_count": opp.validation_count,
            "comment_count": opp.comment_count,
            "created_at": opp.created_at
        }
        for opp in opportunities
    ]


@router.delete("/opportunities/{opportunity_id}")
def delete_opportunity(
    opportunity_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete an opportunity"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    db.delete(opportunity)
    db.commit()

    return {"message": "Opportunity deleted successfully"}


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}


@router.post("/users/{user_id}/promote")
def promote_to_admin(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Promote a user to admin"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )

    user.is_admin = True
    db.commit()

    return {"message": f"User {user.name} promoted to admin"}


@router.post("/users/{user_id}/demote")
def demote_from_admin(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Remove admin status from a user"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself"
        )

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )

    user.is_admin = False
    db.commit()

    return {"message": f"User {user.name} demoted from admin"}


from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus


@router.get("/subscriptions")
def list_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tier_filter: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all subscriptions"""
    query = db.query(
        Subscription,
        User.email,
        User.name
    ).join(User, Subscription.user_id == User.id)

    if tier_filter:
        try:
            tier = SubscriptionTier(tier_filter)
            query = query.filter(Subscription.tier == tier)
        except ValueError:
            pass

    if status_filter:
        try:
            status_enum = SubscriptionStatus(status_filter)
            query = query.filter(Subscription.status == status_enum)
        except ValueError:
            pass

    results = query.order_by(desc(Subscription.created_at)).offset(skip).limit(limit).all()

    return [
        {
            "id": sub.id,
            "user_id": sub.user_id,
            "user_email": email,
            "user_name": name,
            "tier": sub.tier.value,
            "status": sub.status.value,
            "stripe_customer_id": sub.stripe_customer_id,
            "stripe_subscription_id": sub.stripe_subscription_id,
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
            "created_at": sub.created_at
        }
        for sub, email, name in results
    ]


@router.patch("/subscriptions/{subscription_id}/tier")
def update_subscription_tier(
    subscription_id: int,
    tier: str,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Manually update a user's subscription tier (admin override)"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    try:
        new_tier = SubscriptionTier(tier)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {tier}. Valid options: free, pro, business, enterprise"
        )

    subscription.tier = new_tier
    db.commit()

    return {"message": f"Subscription updated to {tier}"}


@router.post("/users/{user_id}/grant-subscription")
def grant_subscription(
    user_id: int,
    tier: str = Query(...),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Grant or create a subscription for a user"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    try:
        new_tier = SubscriptionTier(tier)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {tier}. Valid options: free, pro, business, enterprise"
        )

    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if subscription:
        subscription.tier = new_tier
        subscription.status = SubscriptionStatus.ACTIVE
    else:
        subscription = Subscription(
            user_id=user_id,
            tier=new_tier,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)

    db.commit()

    return {"message": f"Granted {tier} subscription to user {user.name}"}
