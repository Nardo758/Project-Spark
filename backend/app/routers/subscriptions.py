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
    PortalSessionCreate,
    PortalSessionResponse,
    UnlockOpportunityRequest,
    UnlockOpportunityResponse,
    ExportRequest,
    BillingInfo,
    PayPerUnlockRequest,
    PayPerUnlockResponse,
    OpportunityAccessInfo
)
from datetime import datetime, timedelta
from app.core.dependencies import get_current_active_user
from app.services.stripe_service import stripe_service
from app.services.usage_service import usage_service
from app.core.config import settings
from app.services.entitlements import get_opportunity_entitlements
from app.services.audit import log_event

router = APIRouter()


@router.get("/stripe-key")
def get_stripe_publishable_key():
    """Get Stripe publishable key for frontend"""
    from app.services.stripe_service import get_stripe_credentials
    _, publishable_key = get_stripe_credentials()
    if not publishable_key:
        raise HTTPException(
            status_code=500,
            detail="Stripe not configured"
        )
    return {"publishable_key": publishable_key}


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


@router.get("/my-subscription")
def get_my_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get simplified subscription status for frontend"""
    subscription = usage_service.get_or_create_subscription(current_user, db)
    usage = usage_service.get_current_usage(current_user, db)
    limits = stripe_service.get_tier_limits(subscription.tier)
    remaining_unlocks = usage_service.get_remaining_unlocks(current_user, db)

    return {
        "tier": subscription.tier.value if hasattr(subscription.tier, 'value') else subscription.tier,
        "status": subscription.status.value if hasattr(subscription.status, 'value') else subscription.status,
        "views_remaining": remaining_unlocks,
        "views_limit": limits.get("monthly_unlocks", 10),
        "period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        "is_active": subscription.status == SubscriptionStatus.ACTIVE
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
    request: Request,
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

    log_event(
        db,
        action="subscription.checkout_session.create",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="subscription",
        resource_id=str(getattr(subscription, "id", "")),
        metadata={"tier": tier.value, "session_id": session.id},
    )

    return {
        "session_id": session.id,
        "url": session.url
    }


@router.post("/portal", response_model=PortalSessionResponse)
def create_portal_session(
    request: Request,
    portal_data: PortalSessionCreate | None = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe Customer Portal session"""
    subscription = usage_service.get_or_create_subscription(current_user, db)

    return_url = (portal_data.return_url if portal_data else None) or request.query_params.get("return_url")
    if not return_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="return_url is required"
        )

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
    request: Request,
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

    log_event(
        db,
        action="subscription.cancel",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="subscription",
        resource_id=str(getattr(subscription, "id", "")),
        metadata={"at_period_end": at_period_end},
    )

    return {"message": "Subscription canceled successfully"}


@router.post("/unlock", response_model=UnlockOpportunityResponse)
def unlock_opportunity(
    unlock_data: UnlockOpportunityRequest,
    request: Request,
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

    log_event(
        db,
        action="subscription.unlock",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="opportunity",
        resource_id=unlock_data.opportunity_id,
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


@router.get("/access/{opportunity_id}", response_model=OpportunityAccessInfo)
def get_opportunity_access_info(
    opportunity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed access information for an opportunity.
    
    Returns tier-based access status, freshness badge, countdown timer info,
    and whether pay-per-unlock is available.
    """
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    ent = get_opportunity_entitlements(db, opportunity, current_user)
    return {
        "opportunity_id": opportunity_id,
        "age_days": ent.age_days,
        "freshness_badge": ent.freshness_badge,
        "is_accessible": ent.is_accessible,
        "is_unlocked": ent.is_unlocked,
        "unlock_method": ent.unlock_method,
        "days_until_unlock": ent.days_until_unlock,
        "can_pay_to_unlock": ent.can_pay_to_unlock,
        "unlock_price": ent.unlock_price,
    }


@router.post("/pay-per-unlock", response_model=PayPerUnlockResponse)
def create_pay_per_unlock(
    unlock_data: PayPerUnlockRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a payment intent for pay-per-unlock ($15).
    
    Only available for:
    - Free tier users
    - Archive opportunities (91+ days old)
    - Max 5 unlocks per day
    """
    from datetime import timezone
    from sqlalchemy import text
    from app.models.subscription import UnlockedOpportunity
    from app.models.stripe_event import PayPerUnlockAttempt, PayPerUnlockAttemptStatus
    
    opportunity = db.query(Opportunity).filter(Opportunity.id == unlock_data.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    subscription = usage_service.get_or_create_subscription(current_user, db)
    
    # Calculate opportunity age
    now = datetime.now(timezone.utc)
    created_at = opportunity.created_at or now
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_days = (now - created_at).days
    
    # Check if already unlocked
    existing = db.query(UnlockedOpportunity).filter(
        UnlockedOpportunity.user_id == current_user.id,
        UnlockedOpportunity.opportunity_id == unlock_data.opportunity_id
    ).first()
    
    if existing and (not existing.expires_at or now <= existing.expires_at):
        raise HTTPException(
            status_code=400,
            detail="Opportunity already unlocked"
        )
    
    # Check eligibility for pay-per-unlock (free tier only)
    if subscription.tier != SubscriptionTier.FREE:
        raise HTTPException(
            status_code=400,
            detail="Pay-per-unlock is only available for free tier users. Your subscription already includes access to this opportunity."
        )
    
    if age_days < 91:
        raise HTTPException(
            status_code=400,
            detail=f"Pay-per-unlock only available for opportunities 91+ days old. This opportunity is {age_days} days old."
        )

    # Concurrency-safe daily limit (5/day): use a per-user/day advisory lock on Postgres,
    # and count attempts (not just succeeded unlocks) so users can't spam PaymentIntents.
    today = now.date()
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        # Lock scope: (user_id, YYYYMMDD)
        db.execute(
            text("SELECT pg_advisory_xact_lock(:k1, :k2)"),
            {"k1": int(current_user.id), "k2": int(today.strftime("%Y%m%d"))},
        )

    # Re-check already unlocked inside the lock window
    existing2 = db.query(UnlockedOpportunity).filter(
        UnlockedOpportunity.user_id == current_user.id,
        UnlockedOpportunity.opportunity_id == unlock_data.opportunity_id
    ).first()
    if existing2 and (not existing2.expires_at or now <= existing2.expires_at):
        raise HTTPException(status_code=400, detail="Opportunity already unlocked")

    attempts_today = db.query(PayPerUnlockAttempt).filter(
        PayPerUnlockAttempt.user_id == current_user.id,
        PayPerUnlockAttempt.attempt_date == today,
        PayPerUnlockAttempt.status.in_([PayPerUnlockAttemptStatus.CREATED, PayPerUnlockAttemptStatus.SUCCEEDED]),
    ).count()

    if attempts_today >= 5:
        raise HTTPException(status_code=429, detail="Daily pay-per-unlock limit reached (5 per day). Try again tomorrow.")
    
    # Get or create Stripe customer
    if not subscription.stripe_customer_id:
        customer = stripe_service.create_customer(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": current_user.id}
        )
        subscription.stripe_customer_id = customer.id
        db.commit()

    # Record attempt before creating PaymentIntent (prevents spamming under concurrency)
    attempt = PayPerUnlockAttempt(
        user_id=current_user.id,
        opportunity_id=unlock_data.opportunity_id,
        attempt_date=today,
        status=PayPerUnlockAttemptStatus.CREATED,
    )
    db.add(attempt)
    db.flush()
    
    # Create payment intent
    try:
        payment_intent = stripe_service.create_payment_intent_for_unlock(
            customer_id=subscription.stripe_customer_id,
            opportunity_id=unlock_data.opportunity_id,
            user_id=current_user.id
        )
    except Exception:
        attempt.status = PayPerUnlockAttemptStatus.CANCELED
        db.commit()
        raise

    attempt.stripe_payment_intent_id = payment_intent.id
    db.commit()

    log_event(
        db,
        action="subscription.pay_per_unlock.intent_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="opportunity",
        resource_id=unlock_data.opportunity_id,
        metadata={"payment_intent_id": payment_intent.id},
    )
    
    return {
        "client_secret": payment_intent.client_secret,
        "payment_intent_id": payment_intent.id,
        "amount": stripe_service.PAY_PER_UNLOCK_PRICE,
        "opportunity_id": unlock_data.opportunity_id
    }


@router.post("/confirm-pay-per-unlock")
def confirm_pay_per_unlock(
    payment_intent_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Confirm a successful pay-per-unlock payment and grant access.
    
    Call this after payment is confirmed on the frontend.
    """
    from datetime import timezone
    from app.models.subscription import UnlockedOpportunity, UnlockMethod
    from app.models.stripe_event import PayPerUnlockAttempt, PayPerUnlockAttemptStatus
    import stripe
    
    # Verify payment intent
    client = stripe_service.get_stripe_client() if hasattr(stripe_service, 'get_stripe_client') else None
    if not client:
        from app.services.stripe_service import get_stripe_client
        client = get_stripe_client()
    
    try:
        payment_intent = client.PaymentIntent.retrieve(payment_intent_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payment intent: {str(e)}")
    
    # Verify payment was successful
    if payment_intent.status != "succeeded":
        raise HTTPException(
            status_code=400,
            detail=f"Payment not completed. Status: {payment_intent.status}"
        )
    
    # Verify metadata
    if payment_intent.metadata.get("type") != "pay_per_unlock":
        raise HTTPException(status_code=400, detail="Invalid payment type")
    
    opportunity_id = int(payment_intent.metadata.get("opportunity_id", 0))
    user_id = int(payment_intent.metadata.get("user_id", 0))
    
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Payment belongs to another user")
    
    # Check if already unlocked with this payment
    existing = db.query(UnlockedOpportunity).filter(
        UnlockedOpportunity.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if existing:
        log_event(
            db,
            action="subscription.pay_per_unlock.confirm_already_unlocked",
            actor=current_user,
            actor_type="user",
            request=request,
            resource_type="opportunity",
            resource_id=opportunity_id,
            metadata={"payment_intent_id": payment_intent_id},
        )
        return {
            "success": True,
            "message": "Already unlocked with this payment",
            "opportunity_id": opportunity_id,
            "expires_at": existing.expires_at.isoformat() if existing.expires_at else None
        }
    
    # Create unlock record with 30-day expiration
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=30)
    
    unlock = UnlockedOpportunity(
        user_id=current_user.id,
        opportunity_id=opportunity_id,
        unlock_method=UnlockMethod.PAY_PER_UNLOCK,
        amount_paid=payment_intent.amount,
        stripe_payment_intent_id=payment_intent_id,
        expires_at=expires_at
    )
    db.add(unlock)
    db.commit()

    attempt = db.query(PayPerUnlockAttempt).filter(
        PayPerUnlockAttempt.stripe_payment_intent_id == payment_intent_id
    ).first()
    if attempt:
        attempt.status = PayPerUnlockAttemptStatus.SUCCEEDED
        db.commit()

    log_event(
        db,
        action="subscription.pay_per_unlock.confirm_succeeded",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="opportunity",
        resource_id=opportunity_id,
        metadata={"payment_intent_id": payment_intent_id, "expires_at": expires_at.isoformat()},
    )
    
    return {
        "success": True,
        "message": "Opportunity unlocked successfully",
        "opportunity_id": opportunity_id,
        "expires_at": expires_at.isoformat(),
        "access_days": 30
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


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    DEPRECATED: Stripe webhook endpoint.

    Canonical endpoint is: POST /api/v1/webhook/stripe (handled by `routers/stripe_webhook.py`).
    We keep this route as a thin forwarder to avoid breaking existing Stripe configs.
    """
    # Import locally to avoid circular imports at module load time.
    from app.routers.stripe_webhook import stripe_webhook as canonical_webhook

    return await canonical_webhook(request=request, db=db)
