"""
Public API Router - January 2026

Rate-limited public API endpoints for Business Track teams.
Authenticated via API key in X-API-Key header.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.services import api_key_service
from app.models.team import Team, TeamApiKey
from app.models.opportunity import Opportunity

router = APIRouter()


class ApiOpportunity(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    ai_opportunity_score: Optional[int] = None
    ai_market_size_estimate: Optional[str] = None
    ai_target_audience: Optional[str] = None
    ai_competition_level: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApiOpportunityList(BaseModel):
    opportunities: List[ApiOpportunity]
    total: int
    page: int
    limit: int


def get_api_key_auth(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> tuple:
    """Validate API key and check rate limits."""
    is_valid, team, api_key, error = api_key_service.validate_api_key(x_api_key, db)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "API-Key"}
        )
    
    # Check rate limit
    is_allowed, remaining = api_key_service.check_rate_limit(team.id, team.api_rate_limit)
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"X-RateLimit-Remaining": "0", "Retry-After": "60"}
        )
    
    return team, api_key, remaining


@router.get("/opportunities", response_model=ApiOpportunityList)
def list_opportunities(
    page: int = 1,
    limit: int = 20,
    category: Optional[str] = None,
    city: Optional[str] = None,
    min_score: Optional[int] = None,
    auth: tuple = Depends(get_api_key_auth),
    db: Session = Depends(get_db)
):
    """
    List opportunities via API.
    
    Requires: opportunities:read scope
    """
    team, api_key, rate_remaining = auth
    
    # Check scope
    import json
    scopes = json.loads(api_key.scopes) if api_key.scopes else []
    if "opportunities:read" not in scopes and "*" not in scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not have 'opportunities:read' scope"
        )
    
    # Build query
    query = db.query(Opportunity).filter(
        Opportunity.moderation_status == 'approved'
    )
    
    if category:
        query = query.filter(Opportunity.category == category)
    if city:
        query = query.filter(Opportunity.city.ilike(f"%{city}%"))
    if min_score:
        query = query.filter(Opportunity.ai_opportunity_score >= min_score)
    
    total = query.count()
    
    # Pagination
    offset = (page - 1) * limit
    opportunities = query.order_by(Opportunity.created_at.desc()).offset(offset).limit(limit).all()
    
    return ApiOpportunityList(
        opportunities=[
            ApiOpportunity(
                id=o.id,
                title=o.title,
                category=o.category,
                description=o.description[:500] if o.description else None,
                city=o.city,
                region=o.region,
                ai_opportunity_score=o.ai_opportunity_score,
                ai_market_size_estimate=o.ai_market_size_estimate,
                ai_target_audience=o.ai_target_audience,
                ai_competition_level=o.ai_competition_level,
                created_at=o.created_at
            )
            for o in opportunities
        ],
        total=total,
        page=page,
        limit=limit
    )


@router.get("/opportunities/{opportunity_id}", response_model=ApiOpportunity)
def get_opportunity(
    opportunity_id: int,
    auth: tuple = Depends(get_api_key_auth),
    db: Session = Depends(get_db)
):
    """
    Get a single opportunity by ID.
    
    Requires: opportunities:read scope
    """
    team, api_key, rate_remaining = auth
    
    import json
    scopes = json.loads(api_key.scopes) if api_key.scopes else []
    if "opportunities:read" not in scopes and "*" not in scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not have 'opportunities:read' scope"
        )
    
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id,
        Opportunity.moderation_status == 'approved'
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return ApiOpportunity(
        id=opportunity.id,
        title=opportunity.title,
        category=opportunity.category,
        description=opportunity.description,
        city=opportunity.city,
        region=opportunity.region,
        ai_opportunity_score=opportunity.ai_opportunity_score,
        ai_market_size_estimate=opportunity.ai_market_size_estimate,
        ai_target_audience=opportunity.ai_target_audience,
        ai_competition_level=opportunity.ai_competition_level,
        created_at=opportunity.created_at
    )


@router.get("/categories")
def list_categories(
    auth: tuple = Depends(get_api_key_auth),
    db: Session = Depends(get_db)
):
    """List all available opportunity categories."""
    team, api_key, rate_remaining = auth
    
    categories = db.query(Opportunity.category).filter(
        Opportunity.moderation_status == 'approved',
        Opportunity.category.isnot(None)
    ).distinct().all()
    
    return {
        "categories": [c[0] for c in categories if c[0]],
        "rate_limit_remaining": rate_remaining
    }


@router.get("/stats")
def get_api_stats(
    auth: tuple = Depends(get_api_key_auth),
    db: Session = Depends(get_db)
):
    """Get API usage statistics for the team."""
    team, api_key, rate_remaining = auth
    
    total_opportunities = db.query(Opportunity).filter(
        Opportunity.moderation_status == 'approved'
    ).count()
    
    return {
        "team_id": team.id,
        "team_name": team.name,
        "api_key_name": api_key.name,
        "usage_count": api_key.usage_count,
        "rate_limit": team.api_rate_limit,
        "rate_limit_remaining": rate_remaining,
        "total_opportunities_available": total_opportunities
    }
