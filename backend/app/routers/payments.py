from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import json
import os
from pydantic import BaseModel
from typing import Optional

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.schemas.payment import (
    CreateMicroPaymentIntentRequest,
    CreateProjectPaymentIntentRequest,
    CreatePaymentIntentResponse,
    ConfirmPaymentRequest,
    ConfirmPaymentResponse,
    CreateDeepDivePaymentRequest,
    CreateFastPassPaymentRequest,
)
from app.services.stripe_service import get_stripe_client, StripeService
from app.models.opportunity import Opportunity
from app.models.subscription import UnlockedOpportunity, SubscriptionTier
from app.services.usage_service import usage_service
from app.services.audit import log_event


class CreateCloneCheckoutRequest(BaseModel):
    email: str
    source_business: str
    target_city: str
    target_state: str


router = APIRouter()


def _create_payment_intent_or_503(**kwargs):
    try:
        stripe = get_stripe_client()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment service not configured")
    return stripe.PaymentIntent.create(**kwargs)


@router.post("/micro", response_model=CreatePaymentIntentResponse)
def create_micro_payment_intent(
    payload: CreateMicroPaymentIntentRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    tx = Transaction(
        user_id=current_user.id,
        opportunity_id=payload.opportunity_id,
        expert_id=payload.expert_id,
        type=TransactionType.MICRO_PAYMENT,
        status=TransactionStatus.PENDING,
        currency="usd",
        amount_cents=payload.amount_cents,
        metadata_json=json.dumps({"purpose": payload.purpose, "metadata": payload.metadata}),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    intent = _create_payment_intent_or_503(
        amount=payload.amount_cents,
        currency="usd",
        metadata={
            "type": TransactionType.MICRO_PAYMENT.value,
            "transaction_id": str(tx.id),
            "user_id": str(current_user.id),
            "expert_id": str(payload.expert_id) if payload.expert_id is not None else "",
            "opportunity_id": str(payload.opportunity_id) if payload.opportunity_id is not None else "",
            "purpose": payload.purpose,
        },
        automatic_payment_methods={"enabled": True},
    )

    tx.stripe_payment_intent_id = intent.id
    db.commit()

    log_event(
        db,
        action="payments.micro.intent_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="transaction",
        resource_id=tx.id,
        metadata={"payment_intent_id": intent.id, "amount_cents": payload.amount_cents},
    )

    return CreatePaymentIntentResponse(client_secret=intent.client_secret, payment_intent_id=intent.id, transaction_id=tx.id)


@router.post("/project", response_model=CreatePaymentIntentResponse)
def create_project_payment_intent(
    payload: CreateProjectPaymentIntentRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    tx = Transaction(
        user_id=current_user.id,
        opportunity_id=payload.opportunity_id,
        expert_id=payload.expert_id,
        type=TransactionType.PROJECT_PAYMENT,
        status=TransactionStatus.PENDING,
        currency="usd",
        amount_cents=payload.amount_cents,
        metadata_json=json.dumps({"purpose": payload.purpose, "metadata": payload.metadata}),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    intent = _create_payment_intent_or_503(
        amount=payload.amount_cents,
        currency="usd",
        metadata={
            "type": TransactionType.PROJECT_PAYMENT.value,
            "transaction_id": str(tx.id),
            "user_id": str(current_user.id),
            "expert_id": str(payload.expert_id) if payload.expert_id is not None else "",
            "opportunity_id": str(payload.opportunity_id) if payload.opportunity_id is not None else "",
            "purpose": payload.purpose,
        },
        automatic_payment_methods={"enabled": True},
    )

    tx.stripe_payment_intent_id = intent.id
    db.commit()

    log_event(
        db,
        action="payments.project.intent_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="transaction",
        resource_id=tx.id,
        metadata={"payment_intent_id": intent.id, "amount_cents": payload.amount_cents},
    )

    return CreatePaymentIntentResponse(client_secret=intent.client_secret, payment_intent_id=intent.id, transaction_id=tx.id)


@router.post("/confirm", response_model=ConfirmPaymentResponse)
def confirm_payment(
    payload: ConfirmPaymentRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        stripe = get_stripe_client()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment service not configured")

    try:
        intent = stripe.PaymentIntent.retrieve(payload.payment_intent_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payment intent: {str(e)}")

    tx = db.query(Transaction).filter(Transaction.stripe_payment_intent_id == payload.payment_intent_id).first()
    if tx and tx.user_id is not None and tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Payment belongs to another user")

    status_map = {
        "succeeded": TransactionStatus.SUCCEEDED,
        "requires_payment_method": TransactionStatus.FAILED,
        "canceled": TransactionStatus.CANCELED,
    }
    mapped = status_map.get(intent.status, TransactionStatus.PENDING)

    if tx:
        tx.status = mapped
        db.commit()

    log_event(
        db,
        action="payments.confirm",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="transaction",
        resource_id=(tx.id if tx else None),
        metadata={"payment_intent_id": payload.payment_intent_id, "stripe_status": intent.status},
    )

    return ConfirmPaymentResponse(success=intent.status == "succeeded", status=intent.status, transaction_id=tx.id if tx else None)


@router.post("/deep-dive", response_model=CreatePaymentIntentResponse)
def create_deep_dive_payment_intent(
    payload: CreateDeepDivePaymentRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a payment intent for Deep Dive ($49) - Layer 2 access add-on.
    Only available for Pro tier users who have already unlocked the opportunity.
    """
    # Check user tier
    subscription = usage_service.get_or_create_subscription(current_user, db)
    user_tier = subscription.tier if isinstance(subscription.tier, SubscriptionTier) else SubscriptionTier(subscription.tier)
    
    if user_tier not in [SubscriptionTier.PRO]:
        raise HTTPException(status_code=403, detail="Deep Dive is only available for Builder (Pro) tier subscribers")
    
    # Check opportunity exists and user has base access
    opportunity = db.query(Opportunity).filter(Opportunity.id == payload.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Check if already has Deep Dive
    existing_unlock = db.query(UnlockedOpportunity).filter(
        UnlockedOpportunity.user_id == current_user.id,
        UnlockedOpportunity.opportunity_id == payload.opportunity_id
    ).first()
    
    if existing_unlock and existing_unlock.has_deep_dive:
        raise HTTPException(status_code=400, detail="You already have Deep Dive access for this opportunity")
    
    # Create transaction
    tx = Transaction(
        user_id=current_user.id,
        opportunity_id=payload.opportunity_id,
        type=TransactionType.MICRO_PAYMENT,
        status=TransactionStatus.PENDING,
        currency="usd",
        amount_cents=StripeService.DEEP_DIVE_PRICE,
        metadata_json=json.dumps({"purpose": "deep_dive", "opportunity_id": payload.opportunity_id}),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    
    intent = _create_payment_intent_or_503(
        amount=StripeService.DEEP_DIVE_PRICE,
        currency="usd",
        metadata={
            "type": "deep_dive",
            "transaction_id": str(tx.id),
            "user_id": str(current_user.id),
            "opportunity_id": str(payload.opportunity_id),
            "purpose": "deep_dive",
        },
        automatic_payment_methods={"enabled": True},
    )
    
    tx.stripe_payment_intent_id = intent.id
    db.commit()
    
    log_event(
        db,
        action="payments.deep_dive.intent_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="transaction",
        resource_id=tx.id,
        metadata={"payment_intent_id": intent.id, "opportunity_id": payload.opportunity_id},
    )
    
    return CreatePaymentIntentResponse(client_secret=intent.client_secret, payment_intent_id=intent.id, transaction_id=tx.id)


@router.post("/fast-pass", response_model=CreatePaymentIntentResponse)
def create_fast_pass_payment_intent(
    payload: CreateFastPassPaymentRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a payment intent for Fast Pass ($99) - HOT opportunity early access.
    Only available for Scaler (Business) tier users for opportunities 0-7 days old.
    """
    # Check user tier
    subscription = usage_service.get_or_create_subscription(current_user, db)
    user_tier = subscription.tier if isinstance(subscription.tier, SubscriptionTier) else SubscriptionTier(subscription.tier)
    
    if user_tier not in [SubscriptionTier.BUSINESS]:
        raise HTTPException(status_code=403, detail="Fast Pass is only available for Scaler (Business) tier subscribers")
    
    # Check opportunity exists
    opportunity = db.query(Opportunity).filter(Opportunity.id == payload.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Check if already unlocked
    is_unlocked = usage_service.is_opportunity_unlocked(current_user, payload.opportunity_id, db)
    if is_unlocked:
        raise HTTPException(status_code=400, detail="You already have access to this opportunity")
    
    # Create transaction
    tx = Transaction(
        user_id=current_user.id,
        opportunity_id=payload.opportunity_id,
        type=TransactionType.MICRO_PAYMENT,
        status=TransactionStatus.PENDING,
        currency="usd",
        amount_cents=StripeService.FAST_PASS_PRICE,
        metadata_json=json.dumps({"purpose": "fast_pass", "opportunity_id": payload.opportunity_id}),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    
    intent = _create_payment_intent_or_503(
        amount=StripeService.FAST_PASS_PRICE,
        currency="usd",
        metadata={
            "type": "fast_pass",
            "transaction_id": str(tx.id),
            "user_id": str(current_user.id),
            "opportunity_id": str(payload.opportunity_id),
            "purpose": "fast_pass",
        },
        automatic_payment_methods={"enabled": True},
    )
    
    tx.stripe_payment_intent_id = intent.id
    db.commit()
    
    log_event(
        db,
        action="payments.fast_pass.intent_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="transaction",
        resource_id=tx.id,
        metadata={"payment_intent_id": intent.id, "opportunity_id": payload.opportunity_id},
    )
    
    return CreatePaymentIntentResponse(client_secret=intent.client_secret, payment_intent_id=intent.id, transaction_id=tx.id)


@router.post("/create-clone-checkout")
def create_clone_checkout_session(
    payload: CreateCloneCheckoutRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Create a Stripe Checkout session for guest Clone Analysis purchase ($49).
    No authentication required - email is collected for receipt and results.
    """
    try:
        stripe = get_stripe_client()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment service not configured")
    
    domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
    if domain:
        base_url = f"https://{domain}"
    else:
        base_url = "http://localhost:5000"
    
    success_url = f"{base_url}/build/reports?path=clone&unlock=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{base_url}/build/reports?path=clone&unlock=cancelled"
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Clone Success Analysis - Full Unlock",
                        "description": f"Detailed demographics, competition, and market data for locations matching {payload.source_business} in {payload.target_city}, {payload.target_state}",
                    },
                    "unit_amount": 4900,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=payload.email,
            metadata={
                "type": "clone_analysis",
                "email": payload.email,
                "source_business": payload.source_business,
                "target_city": payload.target_city,
                "target_state": payload.target_state,
            },
        )
        
        return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")


@router.get("/verify-clone-checkout")
def verify_clone_checkout_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """
    Verify a Stripe Checkout session for Clone Analysis and confirm payment was successful.
    Returns success status and session metadata.
    """
    try:
        stripe = get_stripe_client()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment service not configured")
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == "paid":
            metadata = session.metadata or {}
            return {
                "success": True,
                "payment_status": session.payment_status,
                "email": session.customer_email,
                "source_business": metadata.get("source_business", ""),
                "target_city": metadata.get("target_city", ""),
                "target_state": metadata.get("target_state", ""),
                "amount_total": session.amount_total,
            }
        else:
            return {
                "success": False,
                "payment_status": session.payment_status,
                "message": "Payment not completed"
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid session: {str(e)}")
