"""
Subscriptions Router

Endpoints for managing subscriptions, billing, and usage
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
import csv
import io
import json

from app.db.database import get_db
from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.subscription import SubscriptionTier, SubscriptionStatus
from app.schemas.subscription import (
    SubscriptionResponse,
    SubscriptionLimits,
    UsageStats,
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    PortalSessionResponse,
    UnlockOpportunityRequest,
    UnlockOpportunityResponse,
    ExportRequest,
    BillingInfo
)
from app.core.dependencies import get_current_active_user
from app.services.stripe_service import stripe_service
from app.services.usage_service import usage_service
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=BillingInfo)
def get_billing_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's billing and subscription information"""
    subscription = usage_service.get_or_create_subscription(current_user, db)
    usage = usage_service.get_current_usage(current_user, db)

    limits = stripe_service.get_tier_limits(subscription.tier)

    return {
        "stripe_customer_id": subscription.stripe_customer_id,
        "has_payment_method": subscription.stripe_customer_id is not None,
        "subscription": subscription,
        "usage": {
            **usage.__dict__,
            "limits": limits
        }
    }


@router.get("/limits", response_model=SubscriptionLimits)
def get_subscription_limits(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current subscription tier limits"""
    subscription = usage_service.get_or_create_subscription(current_user, db)
    return stripe_service.get_tier_limits(subscription.tier)


@router.get("/usage", response_model=UsageStats)
def get_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current usage statistics"""
    subscription = usage_service.get_or_create_subscription(current_user, db)
    usage = usage_service.get_current_usage(current_user, db)
    limits = stripe_service.get_tier_limits(subscription.tier)

    return {
        **usage.__dict__,
        "limits": limits
    }


@router.post("/checkout", response_model=CheckoutSessionResponse)
def create_checkout_session(
    checkout_data: CheckoutSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe Checkout session for subscription"""
    # Validate tier
    try:
        tier = SubscriptionTier(checkout_data.tier)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subscription tier: {checkout_data.tier}"
        )

    if tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create checkout for free tier"
        )

    if tier == SubscriptionTier.ENTERPRISE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enterprise tier requires custom setup. Please contact sales."
        )

    # Get or create Stripe customer
    subscription = usage_service.get_or_create_subscription(current_user, db)

    if not subscription.stripe_customer_id:
        customer = stripe_service.create_customer(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": current_user.id}
        )
        subscription.stripe_customer_id = customer.id
        db.commit()

    # Get price ID for tier
    price_id = stripe_service.STRIPE_PRICES.get(tier)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe price not configured for this tier"
        )

    # Create checkout session
    session = stripe_service.create_checkout_session(
        customer_id=subscription.stripe_customer_id,
        price_id=price_id,
        success_url=checkout_data.success_url,
        cancel_url=checkout_data.cancel_url,
        metadata={
            "user_id": current_user.id,
            "tier": tier.value
        }
    )

    return {
        "session_id": session.id,
        "url": session.url
    }


@router.post("/portal", response_model=PortalSessionResponse)
def create_portal_session(
    return_url: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe Customer Portal session"""
    subscription = usage_service.get_or_create_subscription(current_user, db)

    if not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found. Please subscribe first."
        )

    session = stripe_service.create_portal_session(
        customer_id=subscription.stripe_customer_id,
        return_url=return_url
    )

    return {"url": session.url}


@router.post("/cancel")
def cancel_subscription(
    at_period_end: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription"""
    subscription = usage_service.get_or_create_subscription(current_user, db)

    if not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel"
        )

    stripe_service.cancel_subscription(
        subscription.stripe_subscription_id,
        at_period_end=at_period_end
    )

    subscription.cancel_at_period_end = at_period_end
    if not at_period_end:
        subscription.status = SubscriptionStatus.CANCELED

    db.commit()

    return {"message": "Subscription canceled successfully"}


@router.post("/unlock", response_model=UnlockOpportunityResponse)
def unlock_opportunity(
    unlock_data: UnlockOpportunityRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlock an opportunity for full viewing"""
    success, message = usage_service.unlock_opportunity(
        current_user,
        unlock_data.opportunity_id,
        db
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )

    remaining = usage_service.get_remaining_unlocks(current_user, db)

    return {
        "success": True,
        "remaining_unlocks": remaining,
        "opportunity_id": unlock_data.opportunity_id
    }


@router.get("/unlocked/{opportunity_id}")
def check_opportunity_unlocked(
    opportunity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if user has unlocked an opportunity"""
    unlocked = usage_service.is_opportunity_unlocked(current_user, opportunity_id, db)
    remaining = usage_service.get_remaining_unlocks(current_user, db)

    return {
        "unlocked": unlocked,
        "remaining_unlocks": remaining
    }


@router.post("/export")
def export_opportunities(
    export_data: ExportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export opportunities based on subscription tier limits"""
    batch_size = len(export_data.opportunity_ids)

    # Check if user can export
    can_export, reason = usage_service.can_export(current_user, batch_size, db)
    if not can_export:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=reason
        )

    # Get opportunities (only unlocked ones)
    opportunities = []
    for opp_id in export_data.opportunity_ids:
        if usage_service.is_opportunity_unlocked(current_user, opp_id, db):
            opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
            if opp:
                opportunities.append(opp)

    if not opportunities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No unlocked opportunities found to export"
        )

    # Record export
    usage_service.record_export(current_user, len(opportunities), db)

    # Generate export
    if export_data.format == "csv":
        return export_csv(opportunities)
    elif export_data.format == "json":
        return export_json(opportunities)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid export format. Use 'csv' or 'json'"
        )


def export_csv(opportunities):
    """Generate CSV export"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "title", "description", "category", "status",
        "validation_count", "comment_count", "created_at"
    ])
    writer.writeheader()

    for opp in opportunities:
        writer.writerow({
            "id": opp.id,
            "title": opp.title,
            "description": opp.description,
            "category": opp.category,
            "status": opp.status,
            "validation_count": opp.validation_count,
            "comment_count": opp.comment_count,
            "created_at": opp.created_at.isoformat() if opp.created_at else ""
        })

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=opportunities.csv"}
    )


def export_json(opportunities):
    """Generate JSON export"""
    data = [{
        "id": opp.id,
        "title": opp.title,
        "description": opp.description,
        "category": opp.category,
        "status": opp.status,
        "validation_count": opp.validation_count,
        "comment_count": opp.comment_count,
        "created_at": opp.created_at.isoformat() if opp.created_at else None
    } for opp in opportunities]

    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=opportunities.json"}
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle the event
    if event.type == "checkout.session.completed":
        handle_checkout_completed(event.data.object, db)
    elif event.type == "customer.subscription.updated":
        handle_subscription_updated(event.data.object, db)
    elif event.type == "customer.subscription.deleted":
        handle_subscription_deleted(event.data.object, db)

    return {"status": "success"}


def handle_checkout_completed(session, db: Session):
    """Handle successful checkout"""
    user_id = session.metadata.get("user_id")
    if not user_id:
        return

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return

    subscription = usage_service.get_or_create_subscription(user, db)
    subscription.stripe_subscription_id = session.subscription
    db.commit()


def handle_subscription_updated(stripe_subscription, db: Session):
    """Handle subscription update"""
    from app.models.subscription import Subscription
    from datetime import datetime

    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription.id
    ).first()

    if not subscription:
        return

    # Update subscription details
    subscription.status = SubscriptionStatus(stripe_subscription.status)
    subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
    subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
    subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end

    # Update tier based on price ID
    price_id = stripe_subscription.items.data[0].price.id
    for tier, pid in stripe_service.STRIPE_PRICES.items():
        if pid == price_id:
            subscription.tier = tier
            break

    db.commit()


def handle_subscription_deleted(stripe_subscription, db: Session):
    """Handle subscription cancellation"""
    from app.models.subscription import Subscription

    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription.id
    ).first()

    if not subscription:
        return

    subscription.tier = SubscriptionTier.FREE
    subscription.status = SubscriptionStatus.CANCELED
    subscription.stripe_subscription_id = None
    db.commit()
