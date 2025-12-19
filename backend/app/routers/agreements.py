"""
Agreements Router

Endpoints for managing success-fee and revenue-share agreements.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.agreement import SuccessFeeAgreement, AgreementType, AgreementStatus, TriggerType
from app.models.expert import Expert
from app.models.success_pattern import SuccessPattern
from pydantic import BaseModel


router = APIRouter(prefix="/agreements", tags=["Agreements"])


class AgreementCreate(BaseModel):
    expert_id: int
    opportunity_id: Optional[int] = None
    agreement_type: str = "success_fee"
    title: Optional[str] = None
    description: Optional[str] = None
    fee_percentage_bps: Optional[int] = None
    fee_cap_cents: Optional[int] = None
    trigger_type: str = "first_revenue"
    trigger_threshold_cents: Optional[int] = None
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class AgreementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fee_percentage_bps: Optional[int] = None
    fee_cap_cents: Optional[int] = None
    trigger_threshold_cents: Optional[int] = None
    expires_at: Optional[datetime] = None


class AgreementResponse(BaseModel):
    id: int
    user_id: int
    expert_id: int
    opportunity_id: Optional[int]
    agreement_type: str
    status: str
    title: Optional[str]
    description: Optional[str]
    fee_percentage_bps: Optional[int]
    fee_cap_cents: Optional[int]
    trigger_type: str
    trigger_threshold_cents: Optional[int]
    payout_split_expert_bps: int
    payout_split_platform_bps: int
    payout_split_escrow_bps: int
    is_triggered: bool
    total_revenue_tracked: float
    total_payouts_made: float
    terms_accepted_by_user: bool
    terms_accepted_by_expert: bool
    starts_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class RecordRevenueRequest(BaseModel):
    amount_cents: int
    description: Optional[str] = None


class TriggerPayoutRequest(BaseModel):
    amount_cents: Optional[int] = None


@router.get("/", response_model=List[AgreementResponse])
def list_agreements(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List user's agreements (as creator or participant)."""
    q = db.query(SuccessFeeAgreement).filter(
        SuccessFeeAgreement.user_id == current_user.id
    )
    
    if status_filter:
        try:
            status_enum = AgreementStatus(status_filter)
            q = q.filter(SuccessFeeAgreement.status == status_enum)
        except ValueError:
            pass
    
    agreements = q.order_by(desc(SuccessFeeAgreement.created_at)).offset(skip).limit(limit).all()
    return agreements


@router.post("/", response_model=AgreementResponse, status_code=status.HTTP_201_CREATED)
def create_agreement(
    payload: AgreementCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new success-fee or revenue-share agreement."""
    expert = db.query(Expert).filter(Expert.id == payload.expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    if not expert.is_active:
        raise HTTPException(status_code=400, detail="Expert is not currently available")
    
    try:
        agreement_type = AgreementType(payload.agreement_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid agreement_type: {payload.agreement_type}")
    
    try:
        trigger_type = TriggerType(payload.trigger_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid trigger_type: {payload.trigger_type}")
    
    agreement = SuccessFeeAgreement(
        user_id=current_user.id,
        expert_id=payload.expert_id,
        opportunity_id=payload.opportunity_id,
        agreement_type=agreement_type,
        status=AgreementStatus.DRAFT,
        title=payload.title or f"Agreement with {expert.name}",
        description=payload.description,
        fee_percentage_bps=payload.fee_percentage_bps or expert.success_fee_bps or 1500,
        fee_cap_cents=payload.fee_cap_cents,
        trigger_type=trigger_type,
        trigger_threshold_cents=payload.trigger_threshold_cents,
        starts_at=payload.starts_at,
        expires_at=payload.expires_at,
        terms_accepted_by_user=True,
    )
    
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    
    return agreement


@router.get("/{agreement_id}", response_model=AgreementResponse)
def get_agreement(
    agreement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get agreement details."""
    agreement = db.query(SuccessFeeAgreement).filter(
        SuccessFeeAgreement.id == agreement_id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    if agreement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return agreement


@router.put("/{agreement_id}", response_model=AgreementResponse)
def update_agreement(
    agreement_id: int,
    payload: AgreementUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update an agreement (only if still in draft status)."""
    agreement = db.query(SuccessFeeAgreement).filter(
        SuccessFeeAgreement.id == agreement_id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    if agreement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if agreement.status != AgreementStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Can only update draft agreements")
    
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(agreement, key, value)
    
    db.commit()
    db.refresh(agreement)
    
    return agreement


@router.post("/{agreement_id}/submit")
def submit_agreement(
    agreement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit agreement for expert signature."""
    agreement = db.query(SuccessFeeAgreement).filter(
        SuccessFeeAgreement.id == agreement_id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    if agreement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if agreement.status != AgreementStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Agreement already submitted")
    
    agreement.status = AgreementStatus.PENDING_SIGNATURE
    db.commit()
    
    return {"message": "Agreement submitted for expert signature", "status": agreement.status.value}


@router.post("/{agreement_id}/activate")
def activate_agreement(
    agreement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Activate agreement (simulates expert acceptance for now)."""
    agreement = db.query(SuccessFeeAgreement).filter(
        SuccessFeeAgreement.id == agreement_id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    if agreement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if agreement.status not in [AgreementStatus.DRAFT, AgreementStatus.PENDING_SIGNATURE]:
        raise HTTPException(status_code=400, detail="Agreement cannot be activated from current status")
    
    now = datetime.utcnow()
    agreement.status = AgreementStatus.ACTIVE
    agreement.terms_accepted_by_expert = True
    agreement.terms_accepted_at = now
    if not agreement.starts_at:
        agreement.starts_at = now
    
    db.commit()
    
    return {"message": "Agreement activated", "status": agreement.status.value}


@router.post("/{agreement_id}/record-revenue")
def record_revenue(
    agreement_id: int,
    payload: RecordRevenueRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Record revenue towards a success-fee agreement."""
    agreement = db.query(SuccessFeeAgreement).filter(
        SuccessFeeAgreement.id == agreement_id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    if agreement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if agreement.status != AgreementStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Agreement is not active")
    
    revenue_dollars = payload.amount_cents / 100.0
    current_revenue = float(agreement.total_revenue_tracked or 0)
    new_total = current_revenue + revenue_dollars
    agreement.total_revenue_tracked = new_total
    
    should_trigger = False
    if not agreement.is_triggered:
        if agreement.trigger_type == TriggerType.FIRST_REVENUE:
            should_trigger = payload.amount_cents > 0
        elif agreement.trigger_type == TriggerType.REVENUE_THRESHOLD:
            threshold = (agreement.trigger_threshold_cents or 0) / 100.0
            should_trigger = new_total >= threshold
    
    if should_trigger:
        agreement.is_triggered = True
        agreement.triggered_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Revenue recorded",
        "total_revenue_tracked": new_total,
        "is_triggered": agreement.is_triggered,
        "triggered_at": agreement.triggered_at.isoformat() if agreement.triggered_at else None,
    }


@router.post("/{agreement_id}/trigger-payout")
def trigger_payout(
    agreement_id: int,
    payload: TriggerPayoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Trigger a payout based on the agreement terms.
    
    Creates transaction records for:
    - Expert share (70% default)
    - Platform share (10% default)
    - Escrow share (20% default, held for 30 days)
    """
    from app.models.transaction import Transaction, TransactionType, TransactionStatus
    
    agreement = db.query(SuccessFeeAgreement).filter(
        SuccessFeeAgreement.id == agreement_id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    if agreement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if agreement.status != AgreementStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Agreement is not active")
    
    if not agreement.is_triggered:
        raise HTTPException(status_code=400, detail="Agreement trigger conditions not met")
    
    total_revenue = float(agreement.total_revenue_tracked or 0) * 100
    fee_bps = agreement.fee_percentage_bps or 1500
    calculated_fee = int(total_revenue * fee_bps / 10000)
    
    if agreement.fee_cap_cents and calculated_fee > agreement.fee_cap_cents:
        calculated_fee = agreement.fee_cap_cents
    
    payout_amount = payload.amount_cents if payload.amount_cents else calculated_fee
    
    already_paid = float(agreement.total_payouts_made or 0) * 100
    remaining = calculated_fee - int(already_paid)
    
    if payout_amount > remaining:
        payout_amount = remaining
    
    if payout_amount <= 0:
        raise HTTPException(status_code=400, detail="No payout remaining")
    
    expert_share = int(payout_amount * agreement.payout_split_expert_bps / 10000)
    platform_share = int(payout_amount * agreement.payout_split_platform_bps / 10000)
    escrow_share = payout_amount - expert_share - platform_share
    
    tx_expert = Transaction(
        user_id=current_user.id,
        expert_id=agreement.expert_id,
        opportunity_id=agreement.opportunity_id,
        type=TransactionType.SUCCESS_FEE,
        status=TransactionStatus.SUCCEEDED,
        amount_cents=expert_share,
        currency="usd",
        metadata_json=json.dumps({
            "agreement_id": agreement.id,
            "split_type": "expert_share",
            "split_bps": agreement.payout_split_expert_bps,
        }),
    )
    db.add(tx_expert)
    
    tx_platform = Transaction(
        user_id=current_user.id,
        expert_id=agreement.expert_id,
        opportunity_id=agreement.opportunity_id,
        type=TransactionType.SUCCESS_FEE,
        status=TransactionStatus.SUCCEEDED,
        amount_cents=platform_share,
        currency="usd",
        metadata_json=json.dumps({
            "agreement_id": agreement.id,
            "split_type": "platform_share",
            "split_bps": agreement.payout_split_platform_bps,
        }),
    )
    db.add(tx_platform)
    
    if escrow_share > 0:
        tx_escrow = Transaction(
            user_id=current_user.id,
            expert_id=agreement.expert_id,
            opportunity_id=agreement.opportunity_id,
            type=TransactionType.SUCCESS_FEE,
            status=TransactionStatus.PENDING,
            amount_cents=escrow_share,
            currency="usd",
            metadata_json=json.dumps({
                "agreement_id": agreement.id,
                "split_type": "escrow_share",
                "split_bps": agreement.payout_split_escrow_bps,
                "escrow_release_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            }),
        )
        db.add(tx_escrow)
    
    agreement.total_payouts_made = (float(agreement.total_payouts_made or 0)) + (payout_amount / 100.0)
    db.commit()
    
    return {
        "message": "Payout processed",
        "total_payout_cents": payout_amount,
        "expert_share_cents": expert_share,
        "platform_share_cents": platform_share,
        "escrow_share_cents": escrow_share,
        "total_payouts_made": float(agreement.total_payouts_made),
        "transactions_created": 3 if escrow_share > 0 else 2,
    }


@router.post("/{agreement_id}/complete")
def complete_agreement(
    agreement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete an agreement and record outcome to success_patterns."""
    agreement = db.query(SuccessFeeAgreement).filter(
        SuccessFeeAgreement.id == agreement_id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    if agreement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if agreement.status not in [AgreementStatus.ACTIVE]:
        raise HTTPException(status_code=400, detail="Agreement cannot be completed from current status")
    
    agreement.status = AgreementStatus.COMPLETED
    
    success_pattern = SuccessPattern(
        user_id=current_user.id,
        opportunity_id=agreement.opportunity_id,
        opportunity_type=agreement.agreement_type.value,
        experts_used=json.dumps([agreement.expert_id]),
        timeline=json.dumps({
            "started_at": agreement.starts_at.isoformat() if agreement.starts_at else None,
            "completed_at": datetime.utcnow().isoformat(),
        }),
        capital_spent=agreement.total_payouts_made,
        revenue_generated=agreement.total_revenue_tracked,
        success_factors=json.dumps([
            "Expert engagement",
            "Success-fee alignment",
        ]),
    )
    db.add(success_pattern)
    db.commit()
    
    return {
        "message": "Agreement completed and outcome recorded",
        "status": agreement.status.value,
        "success_pattern_id": success_pattern.id,
    }


@router.delete("/{agreement_id}")
def cancel_agreement(
    agreement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Cancel an agreement."""
    agreement = db.query(SuccessFeeAgreement).filter(
        SuccessFeeAgreement.id == agreement_id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    if agreement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if agreement.status == AgreementStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot cancel completed agreement")
    
    agreement.status = AgreementStatus.CANCELLED
    db.commit()
    
    return {"message": "Agreement cancelled", "status": agreement.status.value}
