from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.brain import BrainCreate, BrainResponse, BrainSaveOpportunityRequest
from app.services.deepseek_service import deepseek_service
from app.services.json_codec import loads_json

router = APIRouter()


@router.get("/active", response_model=BrainResponse)
def get_active_brain(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    brain = deepseek_service.get_active_brain(db=db, user_id=current_user.id)
    if not brain:
        raise HTTPException(status_code=404, detail="No active brain")

    return BrainResponse(
        id=brain.id,
        name=brain.name,
        focus_tags=loads_json(brain.focus_tags, default=[]),
        match_score=int(brain.match_score or 0),
        knowledge_items=int(brain.knowledge_items or 0),
        tokens_used=int(brain.tokens_used or 0),
        estimated_cost_usd=float(brain.estimated_cost_usd or 0),
    )


@router.post("/", response_model=BrainResponse)
def create_or_update_brain(
    payload: BrainCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Brain name is required")

    focus_tags = [t.strip() for t in payload.focus_tags if isinstance(t, str) and t.strip()]
    brain = deepseek_service.upsert_brain_for_user(db=db, user_id=current_user.id, name=name, focus_tags=focus_tags)

    return BrainResponse(
        id=brain.id,
        name=brain.name,
        focus_tags=loads_json(brain.focus_tags, default=[]),
        match_score=int(brain.match_score or 0),
        knowledge_items=int(brain.knowledge_items or 0),
        tokens_used=int(brain.tokens_used or 0),
        estimated_cost_usd=float(brain.estimated_cost_usd or 0),
    )


@router.post("/save-opportunity", response_model=BrainResponse)
def save_opportunity_to_brain(
    payload: BrainSaveOpportunityRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    brain = deepseek_service.get_active_brain(db=db, user_id=current_user.id)
    if not brain:
        raise HTTPException(status_code=404, detail="No active brain. Create one first.")

    # Minimal server-side "learning": bump knowledge count and score.
    brain.knowledge_items = int(brain.knowledge_items or 0) + 1
    brain.match_score = max(0, min(100, int(brain.match_score or 0) + 5))
    db.commit()
    db.refresh(brain)

    return BrainResponse(
        id=brain.id,
        name=brain.name,
        focus_tags=loads_json(brain.focus_tags, default=[]),
        match_score=int(brain.match_score or 0),
        knowledge_items=int(brain.knowledge_items or 0),
        tokens_used=int(brain.tokens_used or 0),
        estimated_cost_usd=float(brain.estimated_cost_usd or 0),
    )

