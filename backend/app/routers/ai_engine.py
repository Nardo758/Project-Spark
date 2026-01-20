from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.ai_engine import MatchRequest, MatchResponse, RoadmapResponse, ValidationResponse
from app.services.ai_engine import ai_engine_service
from app.services.llm_ai_engine import llm_ai_engine_service
from app.services.ai_costs import record_ai_cost


router = APIRouter()


@router.get("/brain/active")
def get_active_brain(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the user's active AI brain/knowledge base configuration.
    
    This is a placeholder for the future Personal AI Knowledge Base feature.
    Returns disabled state for now.
    """
    return {
        "brainName": None,
        "matchScore": None,
        "tokensUsed": 0,
        "estimatedCostUsd": 0.0,
        "isEnabled": False
    }


@router.post("/match", response_model=MatchResponse)
def match_opportunity(
    payload: MatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        result = llm_ai_engine_service.match_opportunity_to_user_llm(
            db, current_user, payload.opportunity_id, use_llm=True
        )
        usage = result.pop("ai_usage", None)
        provider = result.pop("ai_provider", None)
        if usage and provider:
            record_ai_cost(
                db,
                user_id=current_user.id,
                provider=provider,
                endpoint="ai_engine.match",
                task_type="expert_matching",
                usage=usage,
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/roadmap", response_model=RoadmapResponse)
def generate_roadmap(
    payload: MatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        result = llm_ai_engine_service.generate_roadmap_llm(
            db, current_user, payload.opportunity_id, use_llm=True
        )
        usage = result.pop("ai_usage", None)
        provider = result.pop("ai_provider", None)
        if usage and provider:
            record_ai_cost(
                db,
                user_id=current_user.id,
                provider=provider,
                endpoint="ai_engine.roadmap",
                task_type="business_plan_generation",
                usage=usage,
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/validate", response_model=ValidationResponse)
def validate_opportunity(
    payload: MatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        result = llm_ai_engine_service.validate_opportunity_llm(
            db, current_user, payload.opportunity_id, use_llm=True
        )
        usage = result.pop("ai_usage", None)
        provider = result.pop("ai_provider", None)
        if usage and provider:
            record_ai_cost(
                db,
                user_id=current_user.id,
                provider=provider,
                endpoint="ai_engine.validate",
                task_type="opportunity_validation",
                usage=usage,
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

