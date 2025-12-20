from pydantic import BaseModel, Field
from typing import List


class BrainCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    focus_tags: List[str] = Field(default_factory=list)


class BrainResponse(BaseModel):
    id: int
    name: str
    focus_tags: List[str] = Field(default_factory=list)
    match_score: int = Field(ge=0, le=100)
    knowledge_items: int = Field(ge=0)
    tokens_used: int = Field(ge=0)
    estimated_cost_usd: float = Field(ge=0)

    class Config:
        from_attributes = True


class BrainSaveOpportunityRequest(BaseModel):
    opportunity_id: int


class DeepSeekAnalyzeRequest(BaseModel):
    opportunity_id: int
    analysis_type: str = "quick_match"


class DeepSeekAnalyzeResponse(BaseModel):
    match_score: int = Field(ge=0, le=100)
    reasoning: str
    tokens_used: int = Field(ge=0)
    estimated_cost_usd: float = Field(ge=0)

