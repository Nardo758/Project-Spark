"""
Admin Router

Administrative endpoints for managing users, content, and platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
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
    items = q.order_by(desc(IdeaValidation.created_at)).offset(skip).limit(limit).all()
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
