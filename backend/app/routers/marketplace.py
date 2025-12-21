from __future__ import annotations

import json
import random
import string
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_current_user_optional
from app.db.database import get_db
from app.models.lead_marketplace import Lead, LeadPurchase, LeadStatus, LeadView, SavedSearch
from app.models.opportunity import Opportunity
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.user import User
from app.schemas.marketplace import (
    MarketplaceLeadCreateFromOpportunity,
    MarketplaceLeadDetail,
    MarketplaceLeadListResponse,
    MarketplaceLeadPublic,
    MarketplacePurchasesResponse,
    MarketplaceSavedSearch,
    MarketplaceSavedSearchCreate,
)
from app.services.audit import log_event
from app.services.stripe_service import get_stripe_client


router = APIRouter()


def _gen_public_id(prefix: str = "LD") -> str:
    suffix = "".join(random.choice(string.digits) for _ in range(5))
    return f"{prefix}-{suffix}"


def _create_payment_intent_or_503(**kwargs):
    try:
        stripe = get_stripe_client()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Payment service not configured")
    return stripe.PaymentIntent.create(**kwargs)


@router.get("/marketplace/leads", response_model=MarketplaceLeadListResponse)
def list_marketplace_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(24, ge=1, le=100),
    q: Optional[str] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    status_filter: str = Query(LeadStatus.ACTIVE.value, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(Lead)

    if status_filter:
        query = query.filter(Lead.status == status_filter)
    if q:
        like = f"%{q}%"
        query = query.filter((Lead.public_title.ilike(like)) | (Lead.anonymized_summary.ilike(like)))
    if industry:
        query = query.filter(Lead.industry == industry)
    if location:
        query = query.filter(Lead.location.ilike(f"%{location}%"))

    query = query.order_by(desc(Lead.published_at), desc(Lead.id))
    total = query.count()
    leads = query.offset(skip).limit(limit).all()

    return MarketplaceLeadListResponse(leads=leads, total=total, page=skip // limit + 1, page_size=limit)


@router.get("/marketplace/leads/{lead_id}", response_model=MarketplaceLeadDetail)
def get_marketplace_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    has_purchased = False
    if current_user:
        has_purchased = (
            db.query(LeadPurchase)
            .filter(LeadPurchase.lead_id == lead_id, LeadPurchase.buyer_id == current_user.id, LeadPurchase.payment_status == "completed")
            .first()
            is not None
        )

    # Only return full_data_json to buyers who purchased.
    payload = MarketplaceLeadDetail.model_validate(lead)
    payload.has_purchased = has_purchased
    if not has_purchased:
        payload.full_data_json = None
    return payload


@router.post("/marketplace/leads/{lead_id}/view", status_code=status.HTTP_204_NO_CONTENT)
def track_lead_view(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    session_id = request.headers.get("x-session-id")
    view = LeadView(lead_id=lead_id, user_id=current_user.id if current_user else None, session_id=session_id)
    db.add(view)
    lead.views_count = int(lead.views_count or 0) + 1
    db.commit()
    return None


@router.post("/marketplace/admin/leads/from-opportunity", response_model=MarketplaceLeadPublic)
def admin_create_lead_from_opportunity(
    payload: MarketplaceLeadCreateFromOpportunity,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    opp = db.query(Opportunity).filter(Opportunity.id == payload.opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # Ensure uniqueness for public_id (best-effort).
    public_id = _gen_public_id()
    for _ in range(10):
        if db.query(Lead).filter(Lead.public_id == public_id).first() is None:
            break
        public_id = _gen_public_id()

    lead = Lead(
        opportunity_id=payload.opportunity_id,
        public_id=public_id,
        public_title=payload.public_title,
        anonymized_summary=payload.anonymized_summary,
        industry=payload.industry,
        deal_size_range=payload.deal_size_range,
        location=payload.location,
        revenue_range=payload.revenue_range,
        status=LeadStatus.ACTIVE.value,
        lead_price_cents=payload.lead_price_cents,
        quality_score=payload.quality_score,
        full_data_json=json.dumps(payload.full_data or {}),
        published_at=datetime.utcnow(),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    log_event(
        db,
        action="marketplace.leads.created_from_opportunity",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="lead",
        resource_id=lead.id,
        metadata={"opportunity_id": payload.opportunity_id, "public_id": lead.public_id},
    )

    return lead


@router.post("/marketplace/leads/{lead_id}/purchase-intent", response_model=Dict[str, Any])
def create_lead_purchase_intent(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.status == LeadStatus.ACTIVE.value).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    existing = db.query(LeadPurchase).filter(LeadPurchase.lead_id == lead_id, LeadPurchase.buyer_id == current_user.id).first()
    if existing and existing.payment_status == "completed":
        raise HTTPException(status_code=400, detail="You already purchased this lead")

    tx = Transaction(
        user_id=current_user.id,
        type=TransactionType.MICRO_PAYMENT,
        status=TransactionStatus.PENDING,
        currency="usd",
        amount_cents=int(lead.lead_price_cents),
        metadata_json=json.dumps({"purpose": "lead_purchase", "lead_id": lead_id}),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    intent = _create_payment_intent_or_503(
        amount=int(lead.lead_price_cents),
        currency="usd",
        metadata={
            # Custom type so the webhook can fulfill lead purchases distinctly.
            "type": "lead_purchase",
            "transaction_id": str(tx.id),
            "user_id": str(current_user.id),
            "purpose": "lead_purchase",
            "lead_id": str(lead_id),
        },
        automatic_payment_methods={"enabled": True},
    )

    tx.stripe_payment_intent_id = intent.id
    db.commit()

    # Create/Update purchase row in pending state for visibility.
    if not existing:
        purchase = LeadPurchase(
            lead_id=lead_id,
            buyer_id=current_user.id,
            transaction_id=intent.id,
            payment_provider="stripe",
            payment_status="pending",
            amount_paid_cents=int(lead.lead_price_cents),
        )
        db.add(purchase)
        db.commit()

    log_event(
        db,
        action="marketplace.leads.purchase_intent_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="transaction",
        resource_id=tx.id,
        metadata={"lead_id": lead_id, "payment_intent_id": intent.id, "amount_cents": int(lead.lead_price_cents)},
    )

    return {"client_secret": intent.client_secret, "payment_intent_id": intent.id, "transaction_id": tx.id}


@router.get("/marketplace/me/purchases", response_model=MarketplacePurchasesResponse)
def my_lead_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    purchases = (
        db.query(LeadPurchase)
        .filter(LeadPurchase.buyer_id == current_user.id)
        .order_by(desc(LeadPurchase.purchased_at))
        .all()
    )
    return MarketplacePurchasesResponse(purchases=purchases)


@router.get("/marketplace/me/searches", response_model=list[MarketplaceSavedSearch])
def my_saved_searches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = db.query(SavedSearch).filter(SavedSearch.user_id == current_user.id).order_by(desc(SavedSearch.created_at)).all()
    out: list[MarketplaceSavedSearch] = []
    for r in rows:
        try:
            filters = json.loads(r.filters_json or "{}")
        except Exception:
            filters = {}
        out.append(
            MarketplaceSavedSearch(
                id=r.id,
                name=r.name,
                filters=filters,
                notification_frequency=r.notification_frequency,
                is_active=bool(r.is_active),
                created_at=r.created_at,
            )
        )
    return out


@router.post("/marketplace/me/searches", response_model=MarketplaceSavedSearch, status_code=status.HTTP_201_CREATED)
def create_saved_search(
    payload: MarketplaceSavedSearchCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = SavedSearch(
        user_id=current_user.id,
        name=payload.name,
        filters_json=json.dumps(payload.filters),
        notification_frequency=payload.notification_frequency,
        is_active=payload.is_active,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    log_event(
        db,
        action="marketplace.saved_search.created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="saved_search",
        resource_id=row.id,
        metadata={"name": payload.name},
    )

    return MarketplaceSavedSearch(
        id=row.id,
        name=row.name,
        filters=payload.filters,
        notification_frequency=row.notification_frequency,
        is_active=bool(row.is_active),
        created_at=row.created_at,
    )


@router.delete("/marketplace/me/searches/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = db.query(SavedSearch).filter(SavedSearch.id == search_id, SavedSearch.user_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Saved search not found")
    db.delete(row)
    db.commit()
    return None

