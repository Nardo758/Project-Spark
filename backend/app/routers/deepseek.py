from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.brain import DeepSeekAnalyzeRequest, DeepSeekAnalyzeResponse
from app.services.deepseek_service import deepseek_service

router = APIRouter(prefix="/deepseek", tags=["DeepSeek"])


@router.post("/analyze", response_model=DeepSeekAnalyzeResponse)
def analyze(
    payload: DeepSeekAnalyzeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    brain = deepseek_service.get_active_brain(db=db, user_id=current_user.id)
    if not brain:
        raise HTTPException(status_code=404, detail="No active brain. Create one first.")

    opp = db.query(Opportunity).filter(Opportunity.id == payload.opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    if not deepseek_service.is_configured():
        raise HTTPException(status_code=503, detail="DeepSeek is not configured on the server")

    # For now we only support quick_match (cheap + fast)
    try:
        match_score, reasoning, tokens = deepseek_service.analyze_opportunity_quick_match(brain=brain, opp=opp)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    # Record usage + gently blend match score into the brain's score.
    deepseek_service.record_usage(db=db, brain=brain, tokens=tokens)
    brain.match_score = int(round((int(brain.match_score or 0) * 0.8) + (match_score * 0.2)))
    db.commit()
    db.refresh(brain)

    # This is cost for this single call (display only)
    usd_per_1k = float(os.getenv("DEEPSEEK_USD_PER_1K_TOKENS", "0.001"))
    cost = (tokens / 1000.0) * usd_per_1k
    return DeepSeekAnalyzeResponse(match_score=match_score, reasoning=reasoning, tokens_used=tokens, estimated_cost_usd=cost)

