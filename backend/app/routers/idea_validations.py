"""
Idea Validation Product API

Creates persisted validation records, ties them to Stripe payments, and stores results.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.core.sanitization import sanitize_text
from app.db.database import get_db
from app.models.idea_validation import IdeaValidation, IdeaValidationStatus
from app.models.user import User
from app.schemas.idea_validation import (
    IdeaValidationCreatePaymentIntentRequest,
    IdeaValidationCreatePaymentIntentResponse,
    IdeaValidationDetail,
    IdeaValidationItem,
    IdeaValidationList,
    IdeaValidationRunRequest,
)
from app.services.stripe_service import get_stripe_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/my", response_model=IdeaValidationList)
def list_my_validations(
    skip: int = 0,
    limit: int = 25,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    q = db.query(IdeaValidation).filter(IdeaValidation.user_id == current_user.id)
    total = q.count()
    items = q.order_by(IdeaValidation.created_at.desc()).offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.get("/{idea_validation_id}", response_model=IdeaValidationDetail)
def get_validation(
    idea_validation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    row = db.query(IdeaValidation).filter(IdeaValidation.id == idea_validation_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Validation not found")
    if row.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Not authorized")

    result = None
    result_json_value = getattr(row, 'result_json', None)
    if result_json_value:
        try:
            result = json.loads(str(result_json_value))
        except Exception:
            result = None

    payload = {
        **row.__dict__,
        "result": result,
    }
    # Remove SQLAlchemy internal state if present
    payload.pop("_sa_instance_state", None)
    return payload


@router.post("/create-payment-intent", response_model=IdeaValidationCreatePaymentIntentResponse)
def create_validation_payment_intent(
    req: IdeaValidationCreatePaymentIntentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    safe_idea = sanitize_text(req.idea, max_length=5000) or ""
    safe_title = sanitize_text(req.title, max_length=255) or ""
    safe_category = sanitize_text(req.category, max_length=100) or ""

    if not safe_idea or len(safe_idea) < 10:
        raise HTTPException(status_code=400, detail="Idea is too short")
    if not safe_title or len(safe_title) < 3:
        raise HTTPException(status_code=400, detail="Title is required")
    if not safe_category or len(safe_category) < 2:
        raise HTTPException(status_code=400, detail="Category is required")
    if req.amount_cents < 50:
        raise HTTPException(status_code=400, detail="amount_cents must be >= 50")

    # Create a persisted validation record first
    row = IdeaValidation(
        user_id=current_user.id,
        idea=safe_idea,
        title=safe_title[:255],
        category=safe_category[:100],
        amount_cents=req.amount_cents,
        currency="usd",
        status=IdeaValidationStatus.PENDING_PAYMENT,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    try:
        stripe = get_stripe_client()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment service not configured")

    intent = stripe.PaymentIntent.create(
        amount=req.amount_cents,
        currency="usd",
        metadata={
            # New canonical metadata
            "type": "idea_validation",
            "service": "idea_validation",
            "user_id": str(current_user.id),
            "idea_validation_id": str(row.id),
            "product": "OppGrid Idea Validation",
        },
        automatic_payment_methods={"enabled": True},
    )

    row.stripe_payment_intent_id = intent.id
    db.commit()

    return {
        "idea_validation_id": row.id,
        "client_secret": intent.client_secret,
        "payment_intent_id": intent.id,
        "amount_cents": req.amount_cents,
        "currency": "usd",
    }


@router.post("/{idea_validation_id}/run", response_model=IdeaValidationDetail)
async def run_validation(
    idea_validation_id: int,
    req: IdeaValidationRunRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    row = db.query(IdeaValidation).filter(IdeaValidation.id == idea_validation_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Validation not found")
    if row.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Not authorized")
    stored_intent_id = getattr(row, 'stripe_payment_intent_id', None)
    if not stored_intent_id or stored_intent_id != req.payment_intent_id:
        raise HTTPException(status_code=400, detail="Payment intent does not match this validation")

    # Verify payment intent status (defense in depth; webhook can also mark PAID)
    try:
        stripe = get_stripe_client()
        pi = stripe.PaymentIntent.retrieve(req.payment_intent_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment service not configured")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payment intent: {str(e)}")

    if pi.status != "succeeded":
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=f"Payment not completed. Status: {pi.status}")

    metadata = pi.metadata or {}
    if metadata.get("service") and metadata.get("service") != "idea_validation":
        raise HTTPException(status_code=400, detail="Invalid payment intent for idea validation")
    if metadata.get("idea_validation_id") and metadata.get("idea_validation_id") != str(row.id):
        raise HTTPException(status_code=400, detail="Payment intent does not match validation record")
    if metadata.get("user_id") and metadata.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Payment intent belongs to another user")

    current_status = getattr(row, 'status', None)
    current_result = getattr(row, 'result_json', None)
    if current_status == IdeaValidationStatus.COMPLETED and current_result:
        # Idempotent return
        return get_validation(idea_validation_id, current_user=current_user, db=db)

    # Ensure payment fields/status are up to date even if webhook hasn't run yet.
    if current_status == IdeaValidationStatus.PENDING_PAYMENT:
        row.status = IdeaValidationStatus.PAID  # type: ignore[assignment]
    if not getattr(row, 'amount_cents', None):
        row.amount_cents = pi.get("amount")  # type: ignore[assignment]
    if not getattr(row, 'currency', None):
        row.currency = pi.get("currency", "usd")  # type: ignore[assignment]
    db.commit()

    row.status = IdeaValidationStatus.PROCESSING  # type: ignore[assignment]
    db.commit()

    # Reuse the existing idea_engine validation logic/prompt by importing + calling it.
    from app.routers.idea_engine import VALIDATION_PROMPT, client as anthropic_client

    user_prompt = f"""Validate this business opportunity:

TITLE: {row.title}
CATEGORY: {row.category}

IDEA DESCRIPTION:
{row.idea}

Provide a comprehensive, actionable validation analysis."""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=VALIDATION_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content_block = response.content[0]
        response_text = getattr(content_block, 'text', '') if hasattr(content_block, 'text') else str(content_block)
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        if start_idx == -1 or end_idx <= start_idx:
            raise RuntimeError("Failed to parse validation response")

        json_str = response_text[start_idx:end_idx]
        result = json.loads(json_str)

        # Persist
        row.result_json = json.dumps(result)  # type: ignore[assignment]
        row.opportunity_score = int(result.get("opportunity_score", 0) or 0)  # type: ignore[assignment]
        row.summary = str(result.get("summary", "") or "")[:255]  # type: ignore[assignment]
        row.market_size_estimate = str(result.get("market_size_estimate", "") or "")[:100]  # type: ignore[assignment]
        row.competition_level = str(result.get("competition_level", "") or "")[:50]  # type: ignore[assignment]
        row.urgency_level = str(result.get("urgency_level", "") or "")[:50]  # type: ignore[assignment]
        row.validation_confidence = int(result.get("validation_confidence", 0) or 0)  # type: ignore[assignment]
        row.status = IdeaValidationStatus.COMPLETED  # type: ignore[assignment]
        row.error_message = None  # type: ignore[assignment]
        db.commit()

        return get_validation(idea_validation_id, current_user=current_user, db=db)
    except Exception as e:
        logger.error(f"Idea validation failed: {e}")
        row.status = IdeaValidationStatus.FAILED  # type: ignore[assignment]
        row.error_message = str(e)  # type: ignore[assignment]
        db.commit()
        raise HTTPException(status_code=500, detail="Validation failed")

