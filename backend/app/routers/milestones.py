"""
Milestones Router

Endpoints for managing project milestones tied to agreements or bookings.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import json

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.milestone import Milestone, MilestoneStatus
from app.models.agreement import SuccessFeeAgreement, AgreementStatus
from app.models.booking import ExpertBooking
from pydantic import BaseModel


router = APIRouter(prefix="/milestones", tags=["Milestones"])


class MilestoneCreate(BaseModel):
    agreement_id: Optional[int] = None
    booking_id: Optional[int] = None
    expert_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    order_index: int = 0
    payment_amount_cents: Optional[int] = None
    payment_percentage_bps: Optional[int] = None
    due_date: Optional[datetime] = None
    deliverables: Optional[str] = None


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    payment_amount_cents: Optional[int] = None
    due_date: Optional[datetime] = None
    deliverables: Optional[str] = None


class MilestoneResponse(BaseModel):
    id: int
    agreement_id: Optional[int]
    booking_id: Optional[int]
    user_id: int
    expert_id: Optional[int]
    title: str
    description: Optional[str]
    order_index: int
    status: str
    payment_amount_cents: Optional[int]
    payment_percentage_bps: Optional[int]
    due_date: Optional[datetime]
    started_at: Optional[datetime]
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    paid_at: Optional[datetime]
    deliverables: Optional[str]
    approval_notes: Optional[str]
    rejection_reason: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class SubmitMilestoneRequest(BaseModel):
    deliverables: Optional[str] = None


class ApproveMilestoneRequest(BaseModel):
    approval_notes: Optional[str] = None


class RejectMilestoneRequest(BaseModel):
    reason: str


@router.get("/", response_model=List[MilestoneResponse])
def list_milestones(
    agreement_id: Optional[int] = Query(None),
    booking_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List milestones for the current user."""
    q = db.query(Milestone).filter(Milestone.user_id == current_user.id)
    
    if agreement_id:
        q = q.filter(Milestone.agreement_id == agreement_id)
    if booking_id:
        q = q.filter(Milestone.booking_id == booking_id)
    if status_filter:
        try:
            status_enum = MilestoneStatus(status_filter)
            q = q.filter(Milestone.status == status_enum)
        except ValueError:
            pass
    
    milestones = q.order_by(Milestone.order_index, desc(Milestone.created_at)).offset(skip).limit(limit).all()
    return milestones


@router.post("/", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
def create_milestone(
    payload: MilestoneCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new milestone."""
    if payload.agreement_id:
        agreement = db.query(SuccessFeeAgreement).filter(
            SuccessFeeAgreement.id == payload.agreement_id,
            SuccessFeeAgreement.user_id == current_user.id
        ).first()
        if not agreement:
            raise HTTPException(status_code=404, detail="Agreement not found")
    
    if payload.booking_id:
        booking = db.query(ExpertBooking).filter(
            ExpertBooking.id == payload.booking_id,
            ExpertBooking.user_id == current_user.id
        ).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
    
    milestone = Milestone(
        agreement_id=payload.agreement_id,
        booking_id=payload.booking_id,
        user_id=current_user.id,
        expert_id=payload.expert_id,
        title=payload.title,
        description=payload.description,
        order_index=payload.order_index,
        status=MilestoneStatus.PENDING,
        payment_amount_cents=payload.payment_amount_cents,
        payment_percentage_bps=payload.payment_percentage_bps,
        due_date=payload.due_date,
        deliverables=payload.deliverables,
    )
    
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    
    return milestone


@router.get("/{milestone_id}", response_model=MilestoneResponse)
def get_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get milestone details."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return milestone


@router.put("/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: int,
    payload: MilestoneUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a milestone (only if pending)."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if milestone.status not in [MilestoneStatus.PENDING, MilestoneStatus.REJECTED]:
        raise HTTPException(status_code=400, detail="Can only update pending or rejected milestones")
    
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(milestone, key, value)
    
    db.commit()
    db.refresh(milestone)
    
    return milestone


@router.post("/{milestone_id}/start")
def start_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark a milestone as in progress."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if milestone.status != MilestoneStatus.PENDING:
        raise HTTPException(status_code=400, detail="Milestone is not pending")
    
    milestone.status = MilestoneStatus.IN_PROGRESS
    milestone.started_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Milestone started", "status": milestone.status.value}


@router.post("/{milestone_id}/submit")
def submit_milestone(
    milestone_id: int,
    payload: SubmitMilestoneRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit a milestone for approval."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if milestone.status not in [MilestoneStatus.PENDING, MilestoneStatus.IN_PROGRESS, MilestoneStatus.REJECTED]:
        raise HTTPException(status_code=400, detail="Milestone cannot be submitted from current status")
    
    milestone.status = MilestoneStatus.SUBMITTED
    milestone.submitted_at = datetime.utcnow()
    if payload.deliverables:
        milestone.deliverables = payload.deliverables
    
    db.commit()
    
    return {"message": "Milestone submitted for approval", "status": milestone.status.value}


@router.post("/{milestone_id}/approve")
def approve_milestone(
    milestone_id: int,
    payload: ApproveMilestoneRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Approve a milestone (by user who owns the agreement/booking)."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if milestone.status != MilestoneStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Milestone is not submitted for approval")
    
    milestone.status = MilestoneStatus.APPROVED
    milestone.approved_at = datetime.utcnow()
    milestone.approved_by_user_id = current_user.id
    milestone.approval_notes = payload.approval_notes
    db.commit()
    
    return {"message": "Milestone approved", "status": milestone.status.value}


@router.post("/{milestone_id}/reject")
def reject_milestone(
    milestone_id: int,
    payload: RejectMilestoneRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Reject a milestone and request revisions."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if milestone.status != MilestoneStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Milestone is not submitted for approval")
    
    milestone.status = MilestoneStatus.REJECTED
    milestone.rejection_reason = payload.reason
    db.commit()
    
    return {"message": "Milestone rejected", "status": milestone.status.value}


@router.post("/{milestone_id}/pay")
def pay_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Trigger payment for an approved milestone.
    
    Creates a transaction record and updates milestone status.
    """
    from app.models.transaction import Transaction, TransactionType, TransactionStatus
    
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if milestone.status != MilestoneStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Milestone must be approved before payment")
    
    payment_amount = milestone.payment_amount_cents or 0
    
    if payment_amount > 0:
        tx = Transaction(
            user_id=current_user.id,
            expert_id=milestone.expert_id,
            type=TransactionType.PROJECT_PAYMENT,
            status=TransactionStatus.SUCCEEDED,
            amount_cents=payment_amount,
            currency="usd",
            metadata_json=json.dumps({
                "milestone_id": milestone.id,
                "milestone_title": milestone.title,
                "agreement_id": milestone.agreement_id,
                "booking_id": milestone.booking_id,
            }),
        )
        db.add(tx)
    
    milestone.status = MilestoneStatus.PAID
    milestone.paid_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Milestone payment processed",
        "status": milestone.status.value,
        "amount_cents": payment_amount,
        "transaction_created": payment_amount > 0,
    }


@router.delete("/{milestone_id}")
def delete_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a milestone (only if pending)."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if milestone.status not in [MilestoneStatus.PENDING]:
        raise HTTPException(status_code=400, detail="Can only delete pending milestones")
    
    db.delete(milestone)
    db.commit()
    
    return {"message": "Milestone deleted"}
