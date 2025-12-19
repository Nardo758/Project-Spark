from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.ai_engine import MatchRequest, MatchResponse, RoadmapResponse, ValidationResponse
from app.services.ai_engine import ai_engine_service


router = APIRouter()


@router.post("/match", response_model=MatchResponse)
def match_opportunity(
    payload: MatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        result = ai_engine_service.match_opportunity_to_user(db, current_user, payload.opportunity_id)
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
        result = ai_engine_service.generate_roadmap(db, current_user, payload.opportunity_id)
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
        result = ai_engine_service.validate_opportunity(db, current_user, payload.opportunity_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

