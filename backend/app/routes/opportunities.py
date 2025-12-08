from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.core.database import get_db
from app.schemas.opportunity import Opportunity, OpportunityUpdate
from app.models.opportunity import Opportunity as OpportunityModel, OpportunityStatus, OpportunitySource

router = APIRouter()


@router.get("/", response_model=List[Opportunity])
def get_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    source: Optional[OpportunitySource] = None,
    status: Optional[OpportunityStatus] = None,
    sort_by: str = Query("created_at", regex="^(created_at|friction_score|validation_count)$"),
    db: Session = Depends(get_db)
):
    """Get paginated list of opportunities with filters"""
    query = db.query(OpportunityModel)

    # Apply filters
    if category_id:
        query = query.filter(OpportunityModel.category_id == category_id)
    if source:
        query = query.filter(OpportunityModel.source == source)
    if status:
        query = query.filter(OpportunityModel.status == status)

    # Sort
    if sort_by == "friction_score":
        query = query.order_by(desc(OpportunityModel.friction_score))
    elif sort_by == "validation_count":
        query = query.order_by(desc(OpportunityModel.validation_count))
    else:
        query = query.order_by(desc(OpportunityModel.created_at))

    opportunities = query.offset(skip).limit(limit).all()
    return opportunities


@router.get("/trending", response_model=List[Opportunity])
def get_trending_opportunities(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending opportunities (high validation count)"""
    opportunities = db.query(OpportunityModel).filter(
        OpportunityModel.status == OpportunityStatus.verified
    ).order_by(
        desc(OpportunityModel.validation_count),
        desc(OpportunityModel.friction_score)
    ).limit(limit).all()

    return opportunities


@router.get("/{opportunity_id}", response_model=Opportunity)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    """Get a specific opportunity by ID"""
    opportunity = db.query(OpportunityModel).filter(OpportunityModel.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@router.patch("/{opportunity_id}", response_model=Opportunity)
def update_opportunity(
    opportunity_id: int,
    opportunity_update: OpportunityUpdate,
    db: Session = Depends(get_db)
):
    """Update an opportunity (admin function)"""
    db_opportunity = db.query(OpportunityModel).filter(OpportunityModel.id == opportunity_id).first()

    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # Update fields
    update_data = opportunity_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_opportunity, field, value)

    db.commit()
    db.refresh(db_opportunity)

    return db_opportunity


@router.delete("/{opportunity_id}", status_code=204)
def delete_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    """Delete an opportunity (admin function)"""
    db_opportunity = db.query(OpportunityModel).filter(OpportunityModel.id == opportunity_id).first()

    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    db.delete(db_opportunity)
    db.commit()

    return None
