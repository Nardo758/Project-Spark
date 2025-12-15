from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import json

from app.db.database import get_db
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, Opportunity as OpportunitySchema, OpportunityList, OpportunityGatedResponse
from app.core.dependencies import get_current_active_user, get_current_user_optional
from app.services.badges import award_impact_points
from app.services.usage_service import usage_service

router = APIRouter()
optional_auth = HTTPBearer(auto_error=False)


@router.post("/", response_model=OpportunitySchema, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new opportunity"""
    new_opportunity = Opportunity(
        **opportunity_data.model_dump(),
        author_id=None if opportunity_data.is_anonymous else current_user.id
    )

    db.add(new_opportunity)

    # Award impact points for creating an opportunity (not for anonymous submissions)
    if not opportunity_data.is_anonymous:
        award_impact_points(current_user, 20, db)

    db.commit()
    db.refresh(new_opportunity)

    return new_opportunity


@router.get("/", response_model=OpportunityList)
def get_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status: str = "active",
    sort_by: str = Query("recent", regex="^(recent|trending|validated|market|feasibility)$"),
    geographic_scope: Optional[str] = None,
    country: Optional[str] = None,
    completion_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of opportunities with filtering and pagination"""
    query = db.query(Opportunity).filter(Opportunity.status == status)

    # Filter by category
    if category:
        query = query.filter(Opportunity.category == category)

    # Filter by geographic scope
    if geographic_scope:
        query = query.filter(Opportunity.geographic_scope == geographic_scope)

    # Filter by country
    if country:
        query = query.filter(Opportunity.country.ilike(f"%{country}%"))

    # Filter by completion status
    if completion_status:
        query = query.filter(Opportunity.completion_status == completion_status)

    # Sorting
    if sort_by == "recent":
        query = query.order_by(desc(Opportunity.created_at))
    elif sort_by == "trending":
        query = query.order_by(desc(Opportunity.growth_rate))
    elif sort_by == "validated":
        query = query.order_by(desc(Opportunity.validation_count))
    elif sort_by == "market":
        query = query.order_by(desc(Opportunity.market_size))
    elif sort_by == "feasibility":
        query = query.order_by(desc(Opportunity.feasibility_score))

    total = query.count()
    opportunities = query.offset(skip).limit(limit).all()

    return OpportunityList(
        opportunities=opportunities,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{opportunity_id}", response_model=OpportunityGatedResponse)
async def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    """Get a single opportunity by ID with gated content based on subscription"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Build response with gating logic
    is_authenticated = current_user is not None
    is_unlocked = False
    
    if current_user:
        is_unlocked = usage_service.is_opportunity_unlocked(current_user, opportunity_id, db)
    
    # Create response dict from opportunity
    response_data = {
        "id": opportunity.id,
        "title": opportunity.title,
        "description": opportunity.description,
        "category": opportunity.category,
        "subcategory": opportunity.subcategory,
        "severity": opportunity.severity,
        "market_size": opportunity.market_size,
        "is_anonymous": opportunity.is_anonymous,
        "geographic_scope": opportunity.geographic_scope,
        "country": opportunity.country,
        "region": opportunity.region,
        "city": opportunity.city,
        "validation_count": opportunity.validation_count,
        "growth_rate": opportunity.growth_rate,
        "author_id": opportunity.author_id,
        "status": opportunity.status,
        "completion_status": opportunity.completion_status,
        "solution_description": opportunity.solution_description,
        "solved_at": opportunity.solved_at,
        "solved_by": opportunity.solved_by,
        "feasibility_score": opportunity.feasibility_score,
        "duplicate_of": opportunity.duplicate_of,
        "created_at": opportunity.created_at,
        "updated_at": opportunity.updated_at,
        "source_platform": opportunity.source_platform,
        "source_url": opportunity.source_url,
        "is_unlocked": is_unlocked,
        "is_authenticated": is_authenticated,
        # Always show basic AI fields (hook content)
        "ai_analyzed": opportunity.ai_analyzed,
        "ai_analyzed_at": opportunity.ai_analyzed_at,
        "ai_opportunity_score": opportunity.ai_opportunity_score,
        "ai_summary": opportunity.ai_summary,
        "ai_market_size_estimate": opportunity.ai_market_size_estimate,
        "ai_competition_level": opportunity.ai_competition_level,
        "ai_urgency_level": opportunity.ai_urgency_level,
        "ai_target_audience": opportunity.ai_target_audience,
        "ai_pain_intensity": opportunity.ai_pain_intensity,
    }
    
    # Gate premium AI fields based on unlock status
    if is_unlocked:
        response_data["ai_business_model_suggestions"] = json.loads(opportunity.ai_business_model_suggestions or "[]")
        response_data["ai_competitive_advantages"] = json.loads(opportunity.ai_competitive_advantages or "[]")
        response_data["ai_key_risks"] = json.loads(opportunity.ai_key_risks or "[]")
        response_data["ai_next_steps"] = json.loads(opportunity.ai_next_steps or "[]")
    else:
        # Return None/empty for gated content
        response_data["ai_business_model_suggestions"] = None
        response_data["ai_competitive_advantages"] = None
        response_data["ai_key_risks"] = None
        response_data["ai_next_steps"] = None
    
    return response_data


@router.put("/{opportunity_id}", response_model=OpportunitySchema)
def update_opportunity(
    opportunity_id: int,
    opportunity_data: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an opportunity (only by author)"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    # Check if user is the author
    if opportunity.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this opportunity"
        )

    # Update fields
    update_data = opportunity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)

    db.commit()
    db.refresh(opportunity)

    return opportunity


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an opportunity (only by author)"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    # Check if user is the author
    if opportunity.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this opportunity"
        )

    db.delete(opportunity)
    db.commit()

    return None


@router.get("/search/", response_model=OpportunityList)
def search_opportunities(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search opportunities by title or description"""
    search_term = f"%{q}%"
    query = db.query(Opportunity).filter(
        (Opportunity.title.ilike(search_term)) |
        (Opportunity.description.ilike(search_term))
    )

    total = query.count()
    opportunities = query.offset(skip).limit(limit).all()

    return OpportunityList(
        opportunities=opportunities,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )
