"""
Unified Stripe Webhook Router

Handles all Stripe webhook events and updates the transactions table automatically.
This router consolidates payment_intent, invoice, and subscription events.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import logging
import json

from app.db.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus, UnlockedOpportunity, UnlockMethod
from app.models.stripe_event import (
    StripeWebhookEvent,
    StripeWebhookEventStatus,
    PayPerUnlockAttempt,
    PayPerUnlockAttemptStatus,
)
from app.models.idea_validation import IdeaValidation, IdeaValidationStatus
from app.services.stripe_service import get_stripe_client
from app.services.usage_service import usage_service
from datetime import datetime, timedelta, timezone
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/stripe", tags=["Stripe Webhooks"])


def get_webhook_secret():
    return os.getenv("STRIPE_WEBHOOK_SECRET", "")


@router.post("")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Unified Stripe webhook handler.
    
    Handles:
    - payment_intent.succeeded: Update transaction status, trigger fulfillment
    - payment_intent.payment_failed: Update transaction status to failed
    - invoice.paid: Record subscription payment in transactions
    - invoice.payment_failed: Handle failed subscription payment
    - checkout.session.completed: Link subscription to user
    - customer.subscription.updated: Sync subscription status
    - customer.subscription.deleted: Cancel subscription
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature header")
    
    webhook_secret = get_webhook_secret()
    event_id = None
    event_created = None
    livemode = False
    if not webhook_secret:
        logger.warning("STRIPE_WEBHOOK_SECRET not configured - skipping signature verification")
        try:
            import json
            event_data = json.loads(payload)
            event_id = event_data.get("id")
            event_type = event_data.get("type")
            event_object = event_data.get("data", {}).get("object", {})
            livemode = bool(event_data.get("livemode", False))
            created_raw = event_data.get("created")
            if isinstance(created_raw, (int, float)):
                event_created = datetime.fromtimestamp(created_raw, tz=timezone.utc)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    else:
        try:
            stripe = get_stripe_client()
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            event_id = getattr(event, "id", None)
            event_type = event.type
            event_object = event.data.object
            livemode = bool(getattr(event, "livemode", False))
            created_raw = getattr(event, "created", None)
            if isinstance(created_raw, (int, float)):
                event_created = datetime.fromtimestamp(created_raw, tz=timezone.utc)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Webhook signature verification failed: {str(e)}")
    
    logger.info(f"Processing Stripe webhook: {event_type}")

    # Idempotency: ensure we only process each Stripe event once.
    if event_id:
        existing = db.query(StripeWebhookEvent).filter(StripeWebhookEvent.stripe_event_id == event_id).first()
        if existing and existing.status == StripeWebhookEventStatus.PROCESSED:
            return {"status": "success", "event_type": event_type, "idempotent": True}

        if not existing:
            db.add(
                StripeWebhookEvent(
                    stripe_event_id=event_id,
                    event_type=event_type or "",
                    livemode=livemode,
                    status=StripeWebhookEventStatus.PROCESSING,
                    attempt_count=1,
                    stripe_created_at=event_created,
                )
            )
        else:
            existing.status = StripeWebhookEventStatus.PROCESSING
            existing.attempt_count = (existing.attempt_count or 0) + 1
            existing.event_type = event_type or existing.event_type
            existing.livemode = livemode
            if event_created:
                existing.stripe_created_at = event_created

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    
    try:
        if event_type == "payment_intent.succeeded":
            handle_payment_intent_succeeded(event_object, db)
        elif event_type == "payment_intent.payment_failed":
            handle_payment_intent_failed(event_object, db)
        elif event_type == "invoice.paid":
            handle_invoice_paid(event_object, db)
        elif event_type == "invoice.payment_failed":
            handle_invoice_payment_failed(event_object, db)
        elif event_type == "checkout.session.completed":
            handle_checkout_completed(event_object, db)
        elif event_type == "customer.subscription.updated":
            handle_subscription_updated(event_object, db)
        elif event_type == "customer.subscription.deleted":
            handle_subscription_deleted(event_object, db)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {str(e)}")
        if event_id:
            row = db.query(StripeWebhookEvent).filter(StripeWebhookEvent.stripe_event_id == event_id).first()
            if row:
                row.status = StripeWebhookEventStatus.FAILED
                db.commit()
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

    if event_id:
        row = db.query(StripeWebhookEvent).filter(StripeWebhookEvent.stripe_event_id == event_id).first()
        if row:
            row.status = StripeWebhookEventStatus.PROCESSED
            db.commit()

    return {"status": "success", "event_type": event_type}


def handle_payment_intent_succeeded(payment_intent: dict, db: Session):
    """
    Handle successful payment intent.
    Updates transaction status and triggers fulfillment based on payment type.
    """
    payment_intent_id = payment_intent.get("id")
    metadata = payment_intent.get("metadata", {})
    payment_type = metadata.get("type", "")
    
    logger.info(f"Payment intent succeeded: {payment_intent_id}, type: {payment_type}")
    
    tx = db.query(Transaction).filter(
        Transaction.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if tx:
        tx.status = TransactionStatus.SUCCEEDED
        tx.stripe_charge_id = payment_intent.get("latest_charge")
        db.commit()
        logger.info(f"Updated transaction {tx.id} to SUCCEEDED")
    else:
        user_id = metadata.get("user_id")
        transaction_type = _map_payment_type_to_transaction_type(payment_type)
        
        if user_id and transaction_type:
            tx = Transaction(
                user_id=int(user_id),
                type=transaction_type,
                status=TransactionStatus.SUCCEEDED,
                amount_cents=payment_intent.get("amount"),
                currency=payment_intent.get("currency", "usd"),
                stripe_payment_intent_id=payment_intent_id,
                stripe_charge_id=payment_intent.get("latest_charge"),
                metadata_json=json.dumps(metadata),
            )
            
            if metadata.get("opportunity_id"):
                tx.opportunity_id = int(metadata.get("opportunity_id"))
            if metadata.get("expert_id"):
                tx.expert_id = int(metadata.get("expert_id"))
            
            db.add(tx)
            db.commit()
            logger.info(f"Created new transaction {tx.id} from webhook")
    
    if payment_type == "pay_per_unlock":
        _fulfill_pay_per_unlock(payment_intent, metadata, db)
    elif payment_type == "micro_payment":
        _fulfill_micro_payment(payment_intent, metadata, db)
    elif payment_type == "project_payment":
        _fulfill_project_payment(payment_intent, metadata, db)
    elif payment_type == "idea_validation" or metadata.get("service") == "idea_validation":
        _fulfill_idea_validation(payment_intent, metadata, db)
    elif payment_type == "deep_dive":
        _fulfill_deep_dive(payment_intent, metadata, db)
    elif payment_type == "fast_pass":
        _fulfill_fast_pass(payment_intent, metadata, db)


def handle_payment_intent_failed(payment_intent: dict, db: Session):
    """Handle failed payment intent - update transaction status."""
    payment_intent_id = payment_intent.get("id")
    
    logger.info(f"Payment intent failed: {payment_intent_id}")
    
    tx = db.query(Transaction).filter(
        Transaction.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if tx:
        tx.status = TransactionStatus.FAILED
        error = payment_intent.get("last_payment_error", {})
        if error:
            existing_meta = json.loads(tx.metadata_json) if tx.metadata_json else {}
            existing_meta["payment_error"] = {
                "code": error.get("code"),
                "message": error.get("message"),
                "type": error.get("type"),
            }
            tx.metadata_json = json.dumps(existing_meta)
        db.commit()
        logger.info(f"Updated transaction {tx.id} to FAILED")

    metadata = payment_intent.get("metadata", {}) or {}
    if metadata.get("type") == "pay_per_unlock":
        attempt = db.query(PayPerUnlockAttempt).filter(
            PayPerUnlockAttempt.stripe_payment_intent_id == payment_intent_id
        ).first()
        if attempt:
            attempt.status = PayPerUnlockAttemptStatus.FAILED
            db.commit()

    if metadata.get("type") == "idea_validation" or metadata.get("service") == "idea_validation":
        _fail_idea_validation(payment_intent, metadata, db)


def handle_invoice_paid(invoice: dict, db: Session):
    """
    Handle paid invoice - typically for subscription payments.
    Records the payment in the transactions table.
    """
    invoice_id = invoice.get("id")
    subscription_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    amount_paid = invoice.get("amount_paid", 0)
    
    logger.info(f"Invoice paid: {invoice_id}, subscription: {subscription_id}")
    
    existing = db.query(Transaction).filter(
        Transaction.stripe_invoice_id == invoice_id
    ).first()
    
    if existing:
        logger.info(f"Invoice {invoice_id} already recorded")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()
    
    user_id = subscription.user_id if subscription else None
    
    tx = Transaction(
        user_id=user_id,
        type=TransactionType.SUBSCRIPTION,
        status=TransactionStatus.SUCCEEDED,
        amount_cents=amount_paid,
        currency=invoice.get("currency", "usd"),
        stripe_invoice_id=invoice_id,
        metadata_json=json.dumps({
            "subscription_id": subscription_id,
            "billing_reason": invoice.get("billing_reason"),
            "period_start": invoice.get("period_start"),
            "period_end": invoice.get("period_end"),
        }),
    )
    db.add(tx)
    db.commit()
    logger.info(f"Recorded subscription payment transaction {tx.id}")


def handle_invoice_payment_failed(invoice: dict, db: Session):
    """Handle failed invoice payment."""
    invoice_id = invoice.get("id")
    customer_id = invoice.get("customer")
    
    logger.info(f"Invoice payment failed: {invoice_id}")
    
    tx = Transaction(
        type=TransactionType.SUBSCRIPTION,
        status=TransactionStatus.FAILED,
        amount_cents=invoice.get("amount_due", 0),
        currency=invoice.get("currency", "usd"),
        stripe_invoice_id=invoice_id,
        metadata_json=json.dumps({
            "billing_reason": invoice.get("billing_reason"),
            "attempt_count": invoice.get("attempt_count"),
        }),
    )
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()
    
    if subscription:
        tx.user_id = subscription.user_id
    
    db.add(tx)
    db.commit()
    logger.info(f"Recorded failed invoice transaction {tx.id}")


def handle_checkout_completed(session: dict, db: Session):
    """Handle successful checkout session - link subscription to user."""
    user_id = session.get("metadata", {}).get("user_id")
    subscription_id = session.get("subscription")
    customer_id = session.get("customer")
    tier = session.get("metadata", {}).get("tier")
    
    logger.info(f"Checkout completed for user {user_id}, subscription {subscription_id}")
    
    if not user_id:
        logger.warning("No user_id in checkout session metadata")
        return
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        logger.warning(f"User {user_id} not found")
        return
    
    subscription = usage_service.get_or_create_subscription(user, db)
    subscription.stripe_subscription_id = subscription_id
    subscription.stripe_customer_id = customer_id
    subscription.status = SubscriptionStatus.ACTIVE
    
    if tier:
        try:
            subscription.tier = SubscriptionTier(tier)
        except ValueError:
            logger.warning(f"Invalid tier in metadata: {tier}")
    
    db.commit()
    logger.info(f"Updated subscription for user {user_id}")


def handle_subscription_updated(stripe_subscription: dict, db: Session):
    """Handle subscription update from Stripe."""
    subscription_id = stripe_subscription.get("id")
    status = stripe_subscription.get("status")
    cancel_at_period_end = stripe_subscription.get("cancel_at_period_end", False)
    current_period_end = stripe_subscription.get("current_period_end")
    
    logger.info(f"Subscription updated: {subscription_id}, status: {status}")
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"Subscription {subscription_id} not found in database")
        return
    
    status_map = {
        "active": SubscriptionStatus.ACTIVE,
        "past_due": SubscriptionStatus.PAST_DUE,
        "canceled": SubscriptionStatus.CANCELED,
        "unpaid": SubscriptionStatus.PAST_DUE,
        "trialing": SubscriptionStatus.ACTIVE,
    }
    
    subscription.status = status_map.get(status, SubscriptionStatus.ACTIVE)
    subscription.cancel_at_period_end = cancel_at_period_end
    
    if current_period_end:
        subscription.current_period_end = datetime.fromtimestamp(current_period_end)
    
    price_id = None
    items = stripe_subscription.get("items", {}).get("data", [])
    if items:
        price_id = items[0].get("price", {}).get("id")
    
    if price_id:
        tier = _map_price_to_tier(price_id)
        if tier:
            subscription.tier = tier
    
    db.commit()
    logger.info(f"Updated subscription {subscription_id} in database")


def handle_subscription_deleted(stripe_subscription: dict, db: Session):
    """Handle subscription cancellation from Stripe."""
    subscription_id = stripe_subscription.get("id")
    
    logger.info(f"Subscription deleted: {subscription_id}")
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"Subscription {subscription_id} not found in database")
        return
    
    subscription.tier = SubscriptionTier.FREE
    subscription.status = SubscriptionStatus.CANCELED
    subscription.stripe_subscription_id = None
    db.commit()
    logger.info(f"Canceled subscription for user {subscription.user_id}")


def _map_payment_type_to_transaction_type(payment_type: str) -> TransactionType | None:
    """Map metadata payment type to TransactionType enum."""
    mapping = {
        "micro_payment": TransactionType.MICRO_PAYMENT,
        "project_payment": TransactionType.PROJECT_PAYMENT,
        "pay_per_unlock": TransactionType.PAY_PER_UNLOCK,
        "success_fee": TransactionType.SUCCESS_FEE,
        "revenue_share": TransactionType.REVENUE_SHARE,
    }
    return mapping.get(payment_type)


def _map_price_to_tier(price_id: str) -> SubscriptionTier | None:
    """Map Stripe price ID to subscription tier."""
    price_pro = os.getenv("STRIPE_PRICE_PRO")
    price_business = os.getenv("STRIPE_PRICE_BUSINESS")
    
    if price_id == price_pro:
        return SubscriptionTier.PRO
    elif price_id == price_business:
        return SubscriptionTier.BUSINESS
    return None


def _fulfill_pay_per_unlock(payment_intent: dict, metadata: dict, db: Session):
    """Fulfill pay-per-unlock after successful payment."""
    user_id = metadata.get("user_id")
    opportunity_id = metadata.get("opportunity_id")
    payment_intent_id = payment_intent.get("id")
    
    if not user_id or not opportunity_id:
        logger.warning("Missing user_id or opportunity_id for pay_per_unlock fulfillment")
        return
    
    existing = db.query(UnlockedOpportunity).filter(
        UnlockedOpportunity.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if existing:
        logger.info(f"Opportunity already unlocked with payment {payment_intent_id}")
        return
    
    now = datetime.utcnow()
    expires_at = now + timedelta(days=30)
    
    unlock = UnlockedOpportunity(
        user_id=int(user_id),
        opportunity_id=int(opportunity_id),
        unlock_method=UnlockMethod.PAY_PER_UNLOCK,
        amount_paid=payment_intent.get("amount"),
        stripe_payment_intent_id=payment_intent_id,
        expires_at=expires_at
    )
    db.add(unlock)
    db.commit()
    logger.info(f"Fulfilled pay-per-unlock for user {user_id}, opportunity {opportunity_id}")

    attempt = db.query(PayPerUnlockAttempt).filter(
        PayPerUnlockAttempt.stripe_payment_intent_id == payment_intent_id
    ).first()
    if attempt:
        attempt.status = PayPerUnlockAttemptStatus.SUCCEEDED
        db.commit()


def _fulfill_micro_payment(payment_intent: dict, metadata: dict, db: Session):
    """Fulfill micro-payment (expert quick service)."""
    logger.info(f"Micro-payment fulfilled: {payment_intent.get('id')}")


def _fulfill_project_payment(payment_intent: dict, metadata: dict, db: Session):
    """Fulfill project payment (larger expert engagement)."""
    logger.info(f"Project payment fulfilled: {payment_intent.get('id')}")


def _fulfill_idea_validation(payment_intent: dict, metadata: dict, db: Session):
    """Mark an IdeaValidation record as paid (idempotent)."""
    validation_id = metadata.get("idea_validation_id")
    payment_intent_id = payment_intent.get("id")
    if not validation_id or not payment_intent_id:
        return
    row = db.query(IdeaValidation).filter(IdeaValidation.id == int(validation_id)).first()
    if not row:
        return
    if row.stripe_payment_intent_id and row.stripe_payment_intent_id != payment_intent_id:
        return
    if row.status in (IdeaValidationStatus.PAID, IdeaValidationStatus.PROCESSING, IdeaValidationStatus.COMPLETED):
        return
    row.status = IdeaValidationStatus.PAID
    row.stripe_payment_intent_id = payment_intent_id
    row.amount_cents = payment_intent.get("amount") or row.amount_cents
    row.currency = payment_intent.get("currency") or row.currency
    db.commit()


def _fail_idea_validation(payment_intent: dict, metadata: dict, db: Session):
    """Mark an IdeaValidation record as failed when payment fails."""
    validation_id = metadata.get("idea_validation_id")
    payment_intent_id = payment_intent.get("id")
    if not validation_id or not payment_intent_id:
        return
    row = db.query(IdeaValidation).filter(IdeaValidation.id == int(validation_id)).first()
    if not row:
        return
    if row.stripe_payment_intent_id and row.stripe_payment_intent_id != payment_intent_id:
        return
    if row.status in (IdeaValidationStatus.COMPLETED,):
        return
    row.status = IdeaValidationStatus.FAILED
    row.error_message = "payment_failed"
    db.commit()


def _fulfill_deep_dive(payment_intent: dict, metadata: dict, db: Session):
    """Fulfill Deep Dive ($49) - add Layer 2 access to opportunity."""
    user_id = metadata.get("user_id")
    opportunity_id = metadata.get("opportunity_id")
    payment_intent_id = payment_intent.get("id")
    
    if not user_id or not opportunity_id:
        logger.warning("Missing user_id or opportunity_id for deep_dive fulfillment")
        return
    
    unlock = db.query(UnlockedOpportunity).filter(
        UnlockedOpportunity.user_id == int(user_id),
        UnlockedOpportunity.opportunity_id == int(opportunity_id)
    ).first()
    
    if unlock:
        if unlock.has_deep_dive:
            logger.info(f"Deep Dive already unlocked for user {user_id}, opportunity {opportunity_id}")
            return
        unlock.has_deep_dive = True
        unlock.deep_dive_payment_intent_id = payment_intent_id
        unlock.deep_dive_unlocked_at = datetime.utcnow()
    else:
        unlock = UnlockedOpportunity(
            user_id=int(user_id),
            opportunity_id=int(opportunity_id),
            unlock_method=UnlockMethod.DEEP_DIVE,
            amount_paid=payment_intent.get("amount"),
            stripe_payment_intent_id=payment_intent_id,
            has_deep_dive=True,
            deep_dive_payment_intent_id=payment_intent_id,
            deep_dive_unlocked_at=datetime.utcnow()
        )
        db.add(unlock)
    
    db.commit()
    logger.info(f"Fulfilled Deep Dive for user {user_id}, opportunity {opportunity_id}")


def _fulfill_fast_pass(payment_intent: dict, metadata: dict, db: Session):
    """Fulfill Fast Pass ($99) - unlock HOT opportunity for Business tier."""
    user_id = metadata.get("user_id")
    opportunity_id = metadata.get("opportunity_id")
    payment_intent_id = payment_intent.get("id")
    
    if not user_id or not opportunity_id:
        logger.warning("Missing user_id or opportunity_id for fast_pass fulfillment")
        return
    
    existing = db.query(UnlockedOpportunity).filter(
        UnlockedOpportunity.user_id == int(user_id),
        UnlockedOpportunity.opportunity_id == int(opportunity_id)
    ).first()
    
    if existing:
        logger.info(f"Opportunity already unlocked for user {user_id}, opportunity {opportunity_id}")
        return
    
    now = datetime.utcnow()
    expires_at = now + timedelta(days=30)
    
    unlock = UnlockedOpportunity(
        user_id=int(user_id),
        opportunity_id=int(opportunity_id),
        unlock_method=UnlockMethod.FAST_PASS,
        amount_paid=payment_intent.get("amount"),
        stripe_payment_intent_id=payment_intent_id,
        expires_at=expires_at,
        has_deep_dive=True
    )
    db.add(unlock)
    db.commit()
    logger.info(f"Fulfilled Fast Pass for user {user_id}, opportunity {opportunity_id}")
