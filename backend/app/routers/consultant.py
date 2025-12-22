"""
Consultant Studio API Router
Three-path validation system: Validate Idea, Search Ideas, Identify Location
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.consultant_studio import ConsultantStudioService
from app.models.consultant_activity import ConsultantActivity

router = APIRouter(prefix="/consultant", tags=["Consultant Studio"])


class ValidateIdeaRequest(BaseModel):
    idea_description: str = Field(..., min_length=10, max_length=5000)
    business_context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class ValidateIdeaResponse(BaseModel):
    success: bool
    idea_description: Optional[str] = None
    recommendation: Optional[str] = None
    online_score: Optional[int] = None
    physical_score: Optional[int] = None
    pattern_analysis: Optional[Dict[str, Any]] = None
    viability_report: Optional[Dict[str, Any]] = None
    similar_opportunities: Optional[List[Dict[str, Any]]] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class SearchIdeasRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    min_score: Optional[int] = None
    time_range: Optional[str] = None
    quality_filter: Optional[str] = None
    session_id: Optional[str] = None


class SearchIdeasResponse(BaseModel):
    success: bool
    opportunities: Optional[List[Dict[str, Any]]] = None
    trends: Optional[List[Dict[str, Any]]] = None
    synthesis: Optional[Dict[str, Any]] = None
    total_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class IdentifyLocationRequest(BaseModel):
    city: str = Field(..., min_length=2, max_length=255)
    business_type: str = Field(..., pattern="^(specific_business|retail|multifamily|hospitality)$")
    business_subtype: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class IdentifyLocationResponse(BaseModel):
    success: bool
    city: Optional[str] = None
    business_type: Optional[str] = None
    business_subtype: Optional[str] = None
    geo_analysis: Optional[Dict[str, Any]] = None
    market_report: Optional[Dict[str, Any]] = None
    site_recommendations: Optional[List[Dict[str, Any]]] = None
    from_cache: Optional[bool] = None
    cache_hit_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class ActivityLogResponse(BaseModel):
    id: int
    path: str
    action: str
    result_summary: Optional[str] = None
    ai_model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: str


@router.post("/validate-idea", response_model=ValidateIdeaResponse)
async def validate_idea(
    request: ValidateIdeaRequest,
    db: Session = Depends(get_db),
    user_id: int = 1,
):
    """
    Path 1: Validate Idea - Online vs Physical decision engine
    
    Analyzes a business idea and recommends whether it should be:
    - ONLINE: Digital/remote business model
    - PHYSICAL: Location-based business model
    - HYBRID: Combination of both
    
    Uses DeepSeek for pattern analysis and Claude for viability reports.
    """
    service = ConsultantStudioService(db)
    
    result = await service.validate_idea(
        user_id=user_id,
        idea_description=request.idea_description,
        business_context=request.business_context,
        session_id=request.session_id,
    )
    
    return ValidateIdeaResponse(**result)


@router.post("/search-ideas", response_model=SearchIdeasResponse)
async def search_ideas(
    request: SearchIdeasRequest,
    db: Session = Depends(get_db),
    user_id: int = 1,
):
    """
    Path 2: Search Ideas - Database exploration with trend detection
    
    Searches validated opportunities with AI-powered trend detection.
    Returns opportunities, detected trends, and AI synthesis.
    """
    service = ConsultantStudioService(db)
    
    filters = {
        "query": request.query,
        "category": request.category,
        "min_score": request.min_score,
        "time_range": request.time_range,
        "quality_filter": request.quality_filter,
    }
    
    filters = {k: v for k, v in filters.items() if v is not None}
    
    result = await service.search_ideas(
        user_id=user_id,
        filters=filters,
        session_id=request.session_id,
    )
    
    return SearchIdeasResponse(**result)


@router.post("/identify-location", response_model=IdentifyLocationResponse)
async def identify_location(
    request: IdentifyLocationRequest,
    db: Session = Depends(get_db),
    user_id: int = 1,
):
    """
    Path 3: Identify Location - Geographic intelligence
    
    Analyzes a location for business viability.
    Supports 4 business types:
    - specific_business: Targeted business analysis
    - retail: Retail location analysis
    - multifamily: Multifamily housing analysis
    - hospitality: Hotel/restaurant analysis
    
    Results are cached for 30 days.
    """
    service = ConsultantStudioService(db)
    
    result = await service.identify_location(
        user_id=user_id,
        city=request.city,
        business_type=request.business_type,
        business_subtype=request.business_subtype,
        additional_params=request.additional_params,
        session_id=request.session_id,
    )
    
    return IdentifyLocationResponse(**result)


@router.get("/activity", response_model=List[ActivityLogResponse])
async def get_activity_log(
    limit: int = 20,
    path: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: int = 1,
):
    """Get user's consultant activity history"""
    query = db.query(ConsultantActivity).filter(
        ConsultantActivity.user_id == user_id
    )
    
    if path:
        query = query.filter(ConsultantActivity.path == path)
    
    activities = query.order_by(
        ConsultantActivity.created_at.desc()
    ).limit(limit).all()
    
    return [
        ActivityLogResponse(
            id=a.id,
            path=a.path,
            action=a.action,
            result_summary=a.result_summary,
            ai_model_used=a.ai_model_used,
            processing_time_ms=a.processing_time_ms,
            created_at=a.created_at.isoformat() if a.created_at else "",
        )
        for a in activities
    ]


@router.get("/stats")
async def get_consultant_stats(
    db: Session = Depends(get_db),
    user_id: int = 1,
):
    """Get consultant studio usage statistics"""
    from sqlalchemy import func
    from app.models.detected_trend import DetectedTrend
    from app.models.location_analysis_cache import LocationAnalysisCache
    
    total_activities = db.query(func.count(ConsultantActivity.id)).filter(
        ConsultantActivity.user_id == user_id
    ).scalar() or 0
    
    path_counts = db.query(
        ConsultantActivity.path,
        func.count(ConsultantActivity.id)
    ).filter(
        ConsultantActivity.user_id == user_id
    ).group_by(ConsultantActivity.path).all()
    
    total_trends = db.query(func.count(DetectedTrend.id)).scalar() or 0
    cached_locations = db.query(func.count(LocationAnalysisCache.id)).scalar() or 0
    
    return {
        "total_activities": total_activities,
        "activities_by_path": {path: count for path, count in path_counts},
        "total_trends_detected": total_trends,
        "cached_locations": cached_locations,
    }
