from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import json

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
)
from app.services.stripe_service import get_stripe_client
from app.services.audit import log_event


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

