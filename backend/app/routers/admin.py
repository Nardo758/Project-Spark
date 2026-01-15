"""
Admin Router

Administrative endpoints for managing users, content, and platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone
import os
import httpx

from app.db.database import get_db
from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.validation import Validation
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.partner import PartnerOutreach, PartnerOutreachStatus
from app.models.tracking import TrackingEvent
from app.models.audit_log import AuditLog
from app.schemas.admin import (
    AdminUserListItem,
    AdminUserDetail,
    AdminUserUpdate,
    AdminBanUser,
    AdminStats,
    AdminOpportunityListItem,
    AdminStripeWebhookEventList,
    AdminPayPerUnlockAttemptList,
    AdminIdeaValidationList,
    AdminPartnerOutreach,
    AdminPartnerOutreachCreate,
    AdminPartnerOutreachUpdate,
)
from app.core.dependencies import get_current_admin_user
from app.services.audit import log_event

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


@router.get("/idea-validations", response_model=AdminIdeaValidationList)
def list_idea_validations(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(
        None,
        description="pending_payment|paid|processing|completed|failed",
    ),
    user_id: Optional[int] = Query(None),
    search_title: Optional[str] = Query(None),
    payment_intent: Optional[str] = Query(None, description="Substring match on pi_* id"),
    include_result: bool = Query(False, description="When true, include result_json and error_message"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List persisted Idea Validations for debugging (processing/failed/paid)."""
    from app.models.idea_validation import IdeaValidation, IdeaValidationStatus

    q = db.query(IdeaValidation)

    if status_filter:
        try:
            q = q.filter(IdeaValidation.status == IdeaValidationStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status_filter")

    if user_id is not None:
        q = q.filter(IdeaValidation.user_id == user_id)

    if search_title:
        q = q.filter(IdeaValidation.title.ilike(f"%{search_title}%"))

    if payment_intent:
        q = q.filter(IdeaValidation.stripe_payment_intent_id.ilike(f"%{payment_intent}%"))

    total = q.count()
    rows = q.order_by(desc(IdeaValidation.created_at)).offset(skip).limit(limit).all()

    # Return dicts so we can omit large fields unless explicitly requested.
    items = []
    for iv in rows:
        item = {
            "id": iv.id,
            "user_id": iv.user_id,
            "title": iv.title,
            "category": iv.category,
            "status": iv.status.value if hasattr(iv.status, "value") else str(iv.status),
            "stripe_payment_intent_id": iv.stripe_payment_intent_id,
            "amount_cents": iv.amount_cents,
            "currency": iv.currency,
            "opportunity_score": iv.opportunity_score,
            "validation_confidence": iv.validation_confidence,
            "summary": iv.summary,
            "created_at": iv.created_at,
            "updated_at": iv.updated_at,
        }
        if include_result:
            item["result_json"] = iv.result_json
            item["error_message"] = iv.error_message
        items.append(item)

    return {"items": items, "total": total}


@router.get("/partners", response_model=List[AdminPartnerOutreach])
def list_partners(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None, description="identified|contacted|in_talks|active|paused|rejected"),
    search: Optional[str] = Query(None, description="Substring match on name/category"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    q = db.query(PartnerOutreach)

    if status_filter:
        try:
            q = q.filter(PartnerOutreach.status == PartnerOutreachStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status_filter")

    if search:
        s = f"%{search}%"
        q = q.filter(
            (PartnerOutreach.name.ilike(s)) |
            (PartnerOutreach.category.ilike(s))
        )

    items = q.order_by(desc(PartnerOutreach.created_at)).offset(skip).limit(limit).all()
    return items


@router.post("/partners", response_model=AdminPartnerOutreach, status_code=status.HTTP_201_CREATED)
def create_partner(
    payload: AdminPartnerOutreachCreate,
    request: Request,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    status_value = payload.status or PartnerOutreachStatus.IDENTIFIED.value
    try:
        status_enum = PartnerOutreachStatus(status_value)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

    partner = PartnerOutreach(
        name=payload.name,
        category=payload.category,
        website_url=payload.website_url,
        contact_name=payload.contact_name,
        contact_email=payload.contact_email,
        status=status_enum,
        notes=payload.notes,
    )
    db.add(partner)
    db.commit()
    db.refresh(partner)

    log_event(
        db,
        action="admin.partner.create",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="partner_outreach",
        resource_id=partner.id,
        metadata={"name": partner.name, "status": partner.status.value if hasattr(partner.status, "value") else str(partner.status)},
    )
    return partner


@router.patch("/partners/{partner_id}", response_model=AdminPartnerOutreach)
def update_partner(
    partner_id: int,
    payload: AdminPartnerOutreachUpdate,
    request: Request,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    partner = db.query(PartnerOutreach).filter(PartnerOutreach.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    data = payload.dict(exclude_unset=True)
    if "status" in data and data["status"] is not None:
        try:
            partner.status = PartnerOutreachStatus(data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
        data.pop("status", None)

    for k, v in data.items():
        setattr(partner, k, v)

    db.commit()
    db.refresh(partner)

    log_event(
        db,
        action="admin.partner.update",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="partner_outreach",
        resource_id=partner_id,
        metadata={"fields": list(payload.dict(exclude_unset=True).keys())},
    )
    return partner


@router.delete("/partners/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_partner(
    partner_id: int,
    request: Request,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    partner = db.query(PartnerOutreach).filter(PartnerOutreach.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    name = partner.name
    db.delete(partner)
    db.commit()

    log_event(
        db,
        action="admin.partner.delete",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="partner_outreach",
        resource_id=partner_id,
        metadata={"name": name},
    )
    return None


@router.get("/tracking/summary")
def tracking_summary(
    days: int = Query(7, ge=1, le=90),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(days=days)

    total = db.query(TrackingEvent).filter(TrackingEvent.created_at >= since).count()
    page_views = db.query(TrackingEvent).filter(
        TrackingEvent.created_at >= since,
        TrackingEvent.name == "page_view",
    ).count()

    top_events = db.query(
        TrackingEvent.name,
        func.count(TrackingEvent.id).label("count"),
    ).filter(
        TrackingEvent.created_at >= since
    ).group_by(
        TrackingEvent.name
    ).order_by(
        desc("count")
    ).limit(10).all()

    top_paths = db.query(
        TrackingEvent.path,
        func.count(TrackingEvent.id).label("count"),
    ).filter(
        TrackingEvent.created_at >= since,
        TrackingEvent.path.isnot(None),
    ).group_by(
        TrackingEvent.path
    ).order_by(
        desc("count")
    ).limit(10).all()

    return {
        "days": days,
        "total_events": total,
        "page_views": page_views,
        "top_events": [{"name": name, "count": count} for name, count in top_events],
        "top_paths": [{"path": path, "count": count} for path, count in top_paths],
    }


@router.get("/tracking/events")
def list_tracking_events(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    name: Optional[str] = Query(None),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    q = db.query(TrackingEvent)
    if name:
        q = q.filter(TrackingEvent.name == name)
    total = q.count()
    items = q.order_by(desc(TrackingEvent.created_at)).offset(skip).limit(limit).all()

    def _parse_props(s):
        if not s:
            return None
        try:
            import json
            return json.loads(s)
        except Exception:
            return None

    return {
        "total": total,
        "items": [
            {
                "id": e.id,
                "name": e.name,
                "path": e.path,
                "referrer": e.referrer,
                "user_id": e.user_id,
                "anonymous_id": e.anonymous_id,
                "properties": _parse_props(e.properties),
                "created_at": e.created_at,
            }
            for e in items
        ],
    }


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
    request: Request,
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

    log_event(
        db,
        action="admin.user.ban",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="user",
        resource_id=user_id,
        metadata={"ban_reason": ban_data.ban_reason},
    )

    return {"message": "User banned successfully"}


@router.post("/users/{user_id}/unban")
def unban_user(
    user_id: int,
    request: Request,
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

    log_event(
        db,
        action="admin.user.unban",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="user",
        resource_id=user_id,
    )

    return {"message": "User unbanned successfully"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
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

    log_event(
        db,
        action="admin.user.delete",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="user",
        resource_id=user_id,
    )

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
    request: Request,
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

    log_event(
        db,
        action="admin.opportunity.delete",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="opportunity",
        resource_id=opportunity_id,
        metadata={"title": getattr(opportunity, "title", None)},
    )

    return {"message": "Opportunity deleted successfully"}


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    request: Request,
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

    log_event(
        db,
        action="admin.comment.delete",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="comment",
        resource_id=comment_id,
    )

    return {"message": "Comment deleted successfully"}


@router.post("/users/{user_id}/promote")
def promote_to_admin(
    user_id: int,
    request: Request,
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

    log_event(
        db,
        action="admin.user.promote",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="user",
        resource_id=user_id,
    )

    return {"message": f"User {user.name} promoted to admin"}


@router.post("/users/{user_id}/demote")
def demote_from_admin(
    user_id: int,
    request: Request,
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

    log_event(
        db,
        action="admin.user.demote",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="user",
        resource_id=user_id,
    )

    return {"message": f"User {user.name} demoted from admin"}


@router.get("/audit-logs")
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    if resource_type:
        q = q.filter(AuditLog.resource_type == resource_type)
    if resource_id:
        q = q.filter(AuditLog.resource_id == resource_id)
    total = q.count()
    items = q.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": a.id,
                "actor_user_id": a.actor_user_id,
                "actor_type": a.actor_type,
                "action": a.action,
                "resource_type": a.resource_type,
                "resource_id": a.resource_id,
                "ip_address": a.ip_address,
                "created_at": a.created_at,
                "metadata_json": a.metadata_json,
            }
            for a in items
        ],
    }


@router.get("/job-runs")
def list_job_runs(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    job_name: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, description="running|succeeded|failed"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    from app.models.job_run import JobRun

    q = db.query(JobRun)
    if job_name:
        q = q.filter(JobRun.job_name == job_name)
    if status_filter:
        q = q.filter(JobRun.status == status_filter)
    total = q.count()
    items = q.order_by(desc(JobRun.started_at)).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": r.id,
                "job_name": r.job_name,
                "status": r.status,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "error": r.error,
                "details_json": r.details_json,
            }
            for r in items
        ],
    }


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


@router.get("/map-usage/stats")
def get_map_usage_stats(
    days: int = Query(30, ge=1, le=365),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get map usage statistics for admin dashboard"""
    from datetime import datetime, timedelta
    from app.models.user_map_session import UserMapSession
    from app.models.census_demographics import (
        MarketGrowthTrajectory,
        CensusMigrationFlow,
        CensusServiceArea,
    )
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    total_sessions = db.query(UserMapSession).count()
    recent_sessions = db.query(UserMapSession).filter(
        UserMapSession.created_at >= cutoff_date
    ).count()
    
    unique_users = db.query(func.count(func.distinct(UserMapSession.user_id))).filter(
        UserMapSession.created_at >= cutoff_date
    ).scalar() or 0
    
    growth_trajectories = db.query(MarketGrowthTrajectory).filter(
        MarketGrowthTrajectory.is_active == True
    ).count()
    
    migration_flows = db.query(CensusMigrationFlow).count()
    
    service_areas = db.query(CensusServiceArea).count()
    
    from sqlalchemy import text
    layer_usage_query = db.execute(text("""
        SELECT kv.key as layer_name, COUNT(*) as usage_count
        FROM user_map_sessions, 
             jsonb_each_text(layer_state) AS kv
        WHERE created_at >= :cutoff_date
          AND layer_state IS NOT NULL
          AND kv.value = 'true'
        GROUP BY kv.key
        ORDER BY usage_count DESC
    """), {"cutoff_date": cutoff_date})
    layer_usage = {row.layer_name: row.usage_count for row in layer_usage_query}
    
    daily_sessions = db.query(
        func.date_trunc('day', UserMapSession.created_at).label('date'),
        func.count(UserMapSession.id).label('count')
    ).filter(
        UserMapSession.created_at >= cutoff_date
    ).group_by(
        func.date_trunc('day', UserMapSession.created_at)
    ).order_by(
        func.date_trunc('day', UserMapSession.created_at)
    ).all()
    
    return {
        "total_sessions": total_sessions,
        "recent_sessions": recent_sessions,
        "unique_users": unique_users,
        "growth_trajectories": growth_trajectories,
        "migration_flows": migration_flows,
        "service_areas": service_areas,
        "layer_usage": layer_usage,
        "daily_sessions": [
            {"date": str(d.date), "count": d.count}
            for d in daily_sessions
        ],
        "period_days": days
    }


@router.get("/map-usage/popular-opportunities")
def get_popular_map_opportunities(
    limit: int = Query(10, ge=1, le=50),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get opportunities with most map views/sessions"""
    from app.models.census_demographics import CensusServiceArea
    
    popular = db.query(
        CensusServiceArea.opportunity_id,
        Opportunity.title,
        Opportunity.category,
        CensusServiceArea.signal_count,
        CensusServiceArea.total_population,
        CensusServiceArea.addressable_market_value,
    ).join(
        Opportunity, CensusServiceArea.opportunity_id == Opportunity.id
    ).order_by(
        desc(CensusServiceArea.signal_count)
    ).limit(limit).all()
    
    return {
        "opportunities": [
            {
                "opportunity_id": p.opportunity_id,
                "title": p.title,
                "category": p.category,
                "signal_count": p.signal_count,
                "total_population": p.total_population,
                "addressable_market": p.addressable_market_value,
            }
            for p in popular
        ]
    }


@router.get("/map-usage/growth-trajectories")
def get_growth_trajectories_admin(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all growth trajectory data for admin review"""
    from app.models.census_demographics import MarketGrowthTrajectory
    
    trajectories = db.query(MarketGrowthTrajectory).filter(
        MarketGrowthTrajectory.is_active == True
    ).order_by(desc(MarketGrowthTrajectory.growth_score)).all()
    
    return {
        "trajectories": [
            {
                "id": t.id,
                "city": t.city,
                "state_fips": t.state_fips,
                "geography_name": t.geography_name,
                "growth_category": t.growth_category.value if t.growth_category else None,
                "growth_score": t.growth_score,
                "population_growth_rate": t.population_growth_rate,
                "net_migration_rate": t.net_migration_rate,
                "latitude": float(t.latitude) if t.latitude else None,
                "longitude": float(t.longitude) if t.longitude else None,
            }
            for t in trajectories
        ],
        "total": len(trajectories)
    }


@router.get("/map-usage/migration-flows")
def get_migration_flows_admin(
    limit: int = Query(50, ge=1, le=200),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get top migration flows for admin review"""
    from app.models.census_demographics import CensusMigrationFlow
    
    flows = db.query(CensusMigrationFlow).order_by(
        desc(CensusMigrationFlow.flow_count)
    ).limit(limit).all()
    
    return {
        "flows": [
            {
                "id": f.id,
                "origin_name": f.origin_name,
                "destination_name": f.destination_name,
                "flow_count": f.flow_count,
                "year": f.year,
                "origin_state_fips": f.origin_state_fips,
                "destination_state_fips": f.destination_state_fips,
            }
            for f in flows
        ],
        "total": len(flows)
    }


# ==================== Marketing & User Management ====================

@router.get("/marketing/users")
def get_marketing_users(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    tier_filter: Optional[str] = Query(None, description="free|pro|business|enterprise"),
    verified_only: bool = Query(False),
    has_subscription: Optional[bool] = Query(None),
    created_after: Optional[date] = Query(None),
    created_before: Optional[date] = Query(None),
    search: Optional[str] = Query(None, description="Search by name or email"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get list of users for marketing purposes with filters and pagination"""
    from app.models.subscription import Subscription
    from sqlalchemy.orm import joinedload
    from datetime import datetime, timezone
    
    q = db.query(User).outerjoin(Subscription, User.id == Subscription.user_id).filter(User.is_banned == False)
    
    if verified_only:
        q = q.filter(User.is_verified == True)
    
    if created_after:
        q = q.filter(User.created_at >= datetime.combine(created_after, datetime.min.time()).replace(tzinfo=timezone.utc))
    
    if created_before:
        q = q.filter(User.created_at <= datetime.combine(created_before, datetime.max.time()).replace(tzinfo=timezone.utc))
    
    if search:
        search_term = f"%{search}%"
        q = q.filter((User.name.ilike(search_term)) | (User.email.ilike(search_term)))
    
    if tier_filter:
        tier_lower = tier_filter.lower()
        if tier_lower == "free":
            q = q.filter((Subscription.id == None) | (Subscription.tier == "free"))
        else:
            q = q.filter(Subscription.tier == tier_lower)
    
    total = q.count()
    
    users_with_subs = q.add_columns(Subscription.tier).order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    
    user_list = []
    for row in users_with_subs:
        u = row[0]
        sub_tier = row[1]
        tier = sub_tier.value if sub_tier and hasattr(sub_tier, 'value') else (str(sub_tier) if sub_tier else "free")
            
        user_list.append({
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "tier": tier,
            "is_verified": u.is_verified,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "oauth_provider": u.oauth_provider,
        })
    
    return {
        "users": user_list,
        "total": total,
        "page_size": limit,
        "skip": skip,
    }


@router.get("/marketing/users/export")
def export_marketing_users(
    tier_filter: Optional[str] = Query(None),
    verified_only: bool = Query(False),
    format: str = Query("json", description="json|csv"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Export all users for marketing - returns all matching users"""
    from app.models.subscription import Subscription
    from fastapi.responses import Response
    import csv
    import io
    
    q = db.query(User).outerjoin(Subscription, User.id == Subscription.user_id).filter(
        User.is_banned == False, User.is_active == True
    )
    
    if verified_only:
        q = q.filter(User.is_verified == True)
    
    if tier_filter:
        tier_lower = tier_filter.lower()
        if tier_lower == "free":
            q = q.filter((Subscription.id == None) | (Subscription.tier == "free"))
        else:
            q = q.filter(Subscription.tier == tier_lower)
    
    users_with_subs = q.add_columns(Subscription.tier).order_by(desc(User.created_at)).all()
    
    user_list = []
    for row in users_with_subs:
        u = row[0]
        sub_tier = row[1]
        tier = sub_tier.value if sub_tier and hasattr(sub_tier, 'value') else (str(sub_tier) if sub_tier else "free")
            
        user_list.append({
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "tier": tier,
            "is_verified": u.is_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "oauth_provider": u.oauth_provider or "email",
        })
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "email", "name", "tier", "is_verified", "created_at", "oauth_provider"])
        writer.writeheader()
        writer.writerows(user_list)
        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=oppgrid_users.csv"}
        )
    
    return {"users": user_list, "total": len(user_list)}


@router.post("/marketing/send-campaign")
async def send_marketing_campaign(
    request: Request,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Send marketing email campaign to selected users via Resend"""
    import os
    import resend
    
    body = await request.json()
    user_ids = body.get("user_ids", [])
    subject = body.get("subject", "")
    html_content = body.get("html_content", "")
    text_content = body.get("text_content", "")
    
    if not subject or (not html_content and not text_content):
        raise HTTPException(status_code=400, detail="Subject and content are required")
    
    if not user_ids:
        raise HTTPException(status_code=400, detail="No users selected")
    
    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        raise HTTPException(status_code=500, detail="Email service not configured")
    
    resend.api_key = resend_key
    
    users = db.query(User).filter(User.id.in_(user_ids), User.is_banned == False).all()
    
    sent_count = 0
    failed_count = 0
    errors = []
    
    for user in users:
        try:
            params = {
                "from": "OppGrid <noreply@oppgrid.com>",
                "to": [user.email],
                "subject": subject,
            }
            if html_content:
                params["html"] = html_content.replace("{{name}}", user.name or "there")
            if text_content:
                params["text"] = text_content.replace("{{name}}", user.name or "there")
            
            resend.Emails.send(params)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            errors.append({"user_id": user.id, "email": user.email, "error": str(e)})
    
    log_event(
        db, 
        "marketing_campaign_sent",
        user_id=admin_user.id,
        details={"sent": sent_count, "failed": failed_count, "subject": subject}
    )
    
    return {
        "sent": sent_count,
        "failed": failed_count,
        "errors": errors[:10] if errors else [],
        "message": f"Campaign sent to {sent_count} users"
    }


@router.get("/marketing/stats")
def get_marketing_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get marketing statistics - user growth, tier distribution, etc."""
    from app.models.subscription import Subscription
    from datetime import datetime, timedelta, timezone
    
    total_users = db.query(User).filter(User.is_banned == False).count()
    verified_users = db.query(User).filter(User.is_verified == True, User.is_banned == False).count()
    
    now = datetime.now(timezone.utc)
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)
    
    new_users_7d = db.query(User).filter(User.created_at >= last_7_days, User.is_banned == False).count()
    new_users_30d = db.query(User).filter(User.created_at >= last_30_days, User.is_banned == False).count()
    
    tier_distribution = {"free": 0, "pro": 0, "business": 0, "enterprise": 0}
    subscriptions = db.query(Subscription).all()
    for sub in subscriptions:
        tier = sub.tier.value if hasattr(sub.tier, 'value') else str(sub.tier)
        if tier.lower() in tier_distribution:
            tier_distribution[tier.lower()] += 1
    
    tier_distribution["free"] = total_users - sum([tier_distribution["pro"], tier_distribution["business"], tier_distribution["enterprise"]])
    
    oauth_breakdown = {}
    users_with_oauth = db.query(User).filter(User.oauth_provider != None, User.is_banned == False).all()
    for u in users_with_oauth:
        provider = u.oauth_provider or "email"
        oauth_breakdown[provider] = oauth_breakdown.get(provider, 0) + 1
    oauth_breakdown["email"] = total_users - sum(oauth_breakdown.values())
    
    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "new_users_7d": new_users_7d,
        "new_users_30d": new_users_30d,
        "tier_distribution": tier_distribution,
        "oauth_breakdown": oauth_breakdown,
        "verification_rate": round((verified_users / total_users * 100) if total_users > 0 else 0, 1),
    }


@router.post("/data-pipeline/trigger-scrape")
async def trigger_scrape_pipeline(
    admin_user: User = Depends(get_current_admin_user),
):
    """
    Trigger the Apify scraper to start a new data collection run.
    Returns immediately with run_id. Use /data-pipeline/status to check progress.
    After scraper completes, call /data-pipeline/import-latest to import the data.
    """
    apify_token = os.getenv("APIFY_API_TOKEN", "")
    if not apify_token:
        raise HTTPException(status_code=500, detail="APIFY_API_TOKEN not configured")
    
    actor_id = "trudax/reddit-scraper-lite"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={apify_token}"
    
    run_input = {
        "debugMode": False,
        "maxItems": 200,
        "maxPostCount": 200,
        "maxComments": 0,
        "proxy": {"useApifyProxy": True},
        "scrollTimeout": 40,
        "searchComments": False,
        "searchCommunities": False,
        "searchPosts": True,
        "searchUsers": False,
        "searches": [
            "frustrated with",
            "wish there was",
            "why is it so hard to",
            "anyone else annoyed by",
            "there should be an app for",
            "I hate how",
            "biggest pain point",
            "looking for solution to"
        ],
        "skipComments": True,
        "sort": "relevance",
        "time": "week"
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(run_url, json=run_input)
        
        if response.status_code != 201:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to trigger scraper: {response.status_code} - {response.text}"
            )
        
        run_data = response.json().get("data", {})
        return {
            "status": "started",
            "run_id": run_data.get("id"),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "next_steps": [
                "Wait 5-10 minutes for scraper to complete",
                "Call GET /api/v1/admin/data-pipeline/scrape-status/{run_id} to check progress",
                "Call POST /api/v1/admin/data-pipeline/import-latest to import results"
            ]
        }


@router.get("/data-pipeline/scrape-status/{run_id}")
async def get_scrape_status(
    run_id: str,
    admin_user: User = Depends(get_current_admin_user),
):
    """Check the status of an Apify scraper run"""
    apify_token = os.getenv("APIFY_API_TOKEN", "")
    if not apify_token:
        raise HTTPException(status_code=500, detail="APIFY_API_TOKEN not configured")
    
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={apify_token}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(status_url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Run not found")
        
        run_info = response.json().get("data", {})
        return {
            "run_id": run_id,
            "status": run_info.get("status"),
            "dataset_id": run_info.get("defaultDatasetId"),
            "started_at": run_info.get("startedAt"),
            "finished_at": run_info.get("finishedAt"),
        }


@router.post("/data-pipeline/import-latest")
async def import_latest_data(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Import the latest scraped data from Apify into the database.
    Uses the existing webhook import logic for consistency.
    """
    from app.routers.webhook import fetch_latest_apify_data
    
    try:
        result = await fetch_latest_apify_data(db=db)
        return {
            "status": "completed",
            "result": result,
            "message": "Import completed using existing pipeline"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/data-pipeline/status")
def get_pipeline_status(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get current data pipeline status and recent import stats"""
    total_opportunities = db.query(Opportunity).count()
    
    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_imports = db.query(Opportunity).filter(
        Opportunity.created_at >= last_24h
    ).count()
    
    ai_analyzed = db.query(Opportunity).filter(
        Opportunity.ai_analyzed == True
    ).count()
    
    pending_analysis = db.query(Opportunity).filter(
        Opportunity.ai_analyzed == False
    ).count()
    
    apify_configured = bool(os.getenv("APIFY_API_TOKEN"))
    serpapi_configured = bool(os.getenv("SERPAPI_KEY"))
    census_configured = bool(os.getenv("CENSUS_API_KEY"))
    
    return {
        "total_opportunities": total_opportunities,
        "recent_imports_24h": recent_imports,
        "ai_analyzed": ai_analyzed,
        "pending_analysis": pending_analysis,
        "configuration": {
            "apify": apify_configured,
            "serpapi": serpapi_configured,
            "census": census_configured
        }
    }


@router.post("/data-pipeline/reprocess-google-maps")
async def reprocess_google_maps_opportunities(
    limit: int = Query(10, ge=1, le=50, description="Number of opportunities to reprocess"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Re-analyze Google Maps opportunities with improved AI processing.
    This will regenerate titles and descriptions using the updated AI prompts.
    """
    from app.services.signal_to_opportunity import SignalToOpportunityProcessor
    import json
    
    opportunities = db.query(Opportunity).filter(
        Opportunity.source_platform == 'apify_google_maps'
    ).order_by(desc(Opportunity.created_at)).limit(limit).all()
    
    if not opportunities:
        return {"status": "no_opportunities", "message": "No Google Maps opportunities found"}
    
    processor = SignalToOpportunityProcessor(db)
    
    if not processor.client:
        return {"status": "error", "message": "AI client not configured"}
    
    results = []
    for opp in opportunities:
        try:
            business_idea = {
                'category': opp.category or 'general',
                'primary_keyword': 'services',
                'signal_count': opp.validation_count or 1,
                'sample_titles': [],
                'location': opp.city or 'Unknown'
            }
            
            validation = {
                'confidence_tier': 'VALIDATED' if (opp.ai_opportunity_score or 0) >= 60 else 'WEAK_SIGNAL',
                'validation_score': (opp.ai_opportunity_score or 50) / 100,
                'green_flags': [],
                'red_flags': []
            }
            
            market_estimate = {
                'market_size_category': opp.market_size or 'MEDIUM',
                'potential_customers': 50000,
                'competition_level': opp.ai_competition_level or 'Medium'
            }
            
            old_title = opp.title
            old_description = opp.description[:100] if opp.description else ""
            
            new_title, new_description = processor._ai_polish_opportunity(
                opp.title,
                opp.description or "",
                business_idea,
                validation,
                market_estimate,
                opp.city or 'Unknown'
            )
            
            opp.title = new_title
            opp.description = new_description
            opp.ai_analyzed_at = datetime.now(timezone.utc)
            
            results.append({
                "id": opp.id,
                "old_title": old_title,
                "new_title": new_title,
                "status": "updated"
            })
            
        except Exception as e:
            results.append({
                "id": opp.id,
                "old_title": opp.title,
                "status": "error",
                "error": str(e)
            })
    
    db.commit()
    
    updated_count = sum(1 for r in results if r.get("status") == "updated")
    
    return {
        "status": "completed",
        "total_processed": len(results),
        "updated": updated_count,
        "results": results
    }
