from pydantic import BaseModel, Field
from typing import List, Optional, Any


class MatchRequest(BaseModel):
    opportunity_id: int


class MatchResponse(BaseModel):
    fit_score: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)
    gaps: List[str]
    recommended_experts: List[dict]
    notes: Optional[str] = None


class RoadmapResponse(BaseModel):
    opportunity_id: int
    timeline_weeks: int = Field(..., ge=1)
    milestones: List[dict]
    risks: List[str] = []
    assumptions: Optional[Any] = None


class ValidationResponse(BaseModel):
    opportunity_id: int
    validation_score: int = Field(..., ge=0, le=100)
    verdict: str
    next_steps: List[str]
    key_risks: List[str]

