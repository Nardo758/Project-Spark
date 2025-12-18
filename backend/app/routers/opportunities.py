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
    """Get a single opportunity by ID with gated content based on subscription and time-decay access"""
    from datetime import datetime
    from app.services.stripe_service import stripe_service
    from app.models.subscription import SubscriptionTier
    
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Build response with gating logic
    is_authenticated = current_user is not None
    is_unlocked = False
    user_tier = SubscriptionTier.FREE
    unlock_method = None
    
    if current_user:
        is_unlocked = usage_service.is_opportunity_unlocked(current_user, opportunity_id, db)
        subscription = usage_service.get_or_create_subscription(current_user, db)
        user_tier = subscription.tier if hasattr(subscription.tier, 'value') else SubscriptionTier(subscription.tier)
        
        # Get unlock method if unlocked
        if is_unlocked:
            from app.models.subscription import UnlockedOpportunity
            unlock_record = db.query(UnlockedOpportunity).filter(
                UnlockedOpportunity.user_id == current_user.id,
                UnlockedOpportunity.opportunity_id == opportunity_id
            ).first()
            if unlock_record:
                unlock_method = unlock_record.unlock_method.value if unlock_record.unlock_method else None
    
    # Calculate opportunity age and time-decay access
    from datetime import timezone
    now = datetime.now(timezone.utc)
    created_at = opportunity.created_at
    # Handle both timezone-aware and naive datetimes
    if created_at is None:
        created_at = now
    elif created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_days = (now - created_at).days
    
    # Get freshness badge and access info
    freshness_badge = stripe_service.get_opportunity_freshness_badge(age_days)
    is_accessible = stripe_service.can_access_opportunity_by_age(user_tier, age_days) if is_authenticated else False
    days_until_unlock = stripe_service.get_days_until_unlock(user_tier, age_days) if is_authenticated else stripe_service.get_days_until_unlock(SubscriptionTier.FREE, age_days)
    
    # Check if pay-per-unlock is available (Free tier, 91+ days, not already unlocked)
    can_pay_to_unlock = (
        age_days >= 91 and 
        (not is_authenticated or user_tier == SubscriptionTier.FREE) and
        not is_unlocked
    )
    
    # Determine layer access based on tier
    tier_value = user_tier.value if hasattr(user_tier, 'value') else str(user_tier)
    deep_dive_available = tier_value in ['business', 'enterprise'] and (is_accessible or is_unlocked)
    execution_package_available = tier_value in ['business', 'enterprise'] and (is_accessible or is_unlocked)
    
    # Build access info
    access_info = {
        "age_days": age_days,
        "freshness_badge": freshness_badge,
        "is_accessible": is_accessible or is_unlocked,
        "is_unlocked": is_unlocked,
        "unlock_method": unlock_method,
        "days_until_unlock": days_until_unlock,
        "can_pay_to_unlock": can_pay_to_unlock,
        "unlock_price": stripe_service.PAY_PER_UNLOCK_PRICE if can_pay_to_unlock else None,
        "user_tier": tier_value if is_authenticated else None
    }
    
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
        "access_info": access_info,
        "deep_dive_available": deep_dive_available,
        "execution_package_available": execution_package_available,
        # Always show basic AI fields (Layer 0 - hook content)
        "ai_analyzed": opportunity.ai_analyzed,
        "ai_analyzed_at": opportunity.ai_analyzed_at,
        "ai_opportunity_score": opportunity.ai_opportunity_score,
        "ai_summary": opportunity.ai_summary,
        "ai_market_size_estimate": opportunity.ai_market_size_estimate,
        "ai_competition_level": opportunity.ai_competition_level,
        "ai_urgency_level": opportunity.ai_urgency_level,
        "ai_target_audience": opportunity.ai_target_audience,
        "ai_pain_intensity": opportunity.ai_pain_intensity,
        # AI-generated content fields
        "ai_generated_title": opportunity.ai_generated_title,
        "ai_problem_statement": opportunity.ai_problem_statement,
        # Raw source data
        "raw_source_data": opportunity.raw_source_data,
    }
    
    # Gate Layer 1 content (Problem Overview) based on access
    if is_accessible or is_unlocked:
        response_data["ai_business_model_suggestions"] = json.loads(opportunity.ai_business_model_suggestions or "[]")
        response_data["ai_competitive_advantages"] = json.loads(opportunity.ai_competitive_advantages or "[]")
        response_data["ai_key_risks"] = json.loads(opportunity.ai_key_risks or "[]")
        response_data["ai_next_steps"] = json.loads(opportunity.ai_next_steps or "[]")
    else:
        response_data["ai_business_model_suggestions"] = None
        response_data["ai_competitive_advantages"] = None
        response_data["ai_key_risks"] = None
        response_data["ai_next_steps"] = None
    
    # Layer 2 content (Deep Dive) - only for Business+ tier
    if deep_dive_available:
        response_data["layer_2_content"] = {
            "competitive_landscape": "Full competitive analysis available",
            "tam_sam_som": opportunity.ai_market_size_estimate,
            "geographic_breakdown": opportunity.geographic_scope,
            "trend_trajectory": "growing"
        }
    else:
        response_data["layer_2_content"] = None
    
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
