from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class WorkflowTypeEnum(str, Enum):
    lean_validation = "lean_validation"
    enterprise_b2b = "enterprise_b2b"
    product_market_fit = "product_market_fit"
    custom = "custom"


class WorkflowStatusEnum(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"
    failed = "failed"


class ArtifactTypeEnum(str, Enum):
    interview = "interview"
    survey = "survey"
    competitor_analysis = "competitor_analysis"
    financial_model = "financial_model"
    market_research = "market_research"
    customer_persona = "customer_persona"
    swot_analysis = "swot_analysis"
    notes = "notes"
    ai_insight = "ai_insight"
    custom = "custom"


class EnhancedWorkspaceCreate(BaseModel):
    opportunity_id: int
    workflow_type: WorkflowTypeEnum = WorkflowTypeEnum.lean_validation
    custom_title: Optional[str] = None
    description: Optional[str] = None
    custom_stages: Optional[List[dict]] = None


class EnhancedWorkspaceUpdate(BaseModel):
    custom_title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[WorkflowStatusEnum] = None
    current_stage: Optional[str] = None
    ai_context: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    stage_id: int
    workspace_id: int
    title: str
    description: Optional[str] = None
    is_completed: bool
    sort_order: int
    ai_suggestion: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StageResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    description: Optional[str] = None
    stage_order: int
    status: str
    progress_percent: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tasks: List[TaskResponse] = []

    class Config:
        from_attributes = True


class ArtifactCreate(BaseModel):
    artifact_type: ArtifactTypeEnum
    title: str
    content: Optional[dict] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None


class ArtifactResponse(BaseModel):
    id: int
    workspace_id: int
    artifact_type: str
    title: str
    content: Optional[Any] = None
    summary: Optional[str] = None
    ai_analysis: Optional[Any] = None
    tags: Optional[Any] = None
    source: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EnhancedWorkspaceResponse(BaseModel):
    id: int
    user_id: int
    opportunity_id: int
    workspace_id: Optional[int] = None
    custom_title: Optional[str] = None
    description: Optional[str] = None
    ai_context: Optional[str] = None
    workflow_type: str
    current_stage: Optional[str] = None
    current_phase: Optional[str] = None
    progress_percent: int
    stage_progress: Optional[Any] = None
    ai_research_context: Optional[Any] = None
    ai_recommendations: Optional[Any] = None
    research_summary: Optional[Any] = None
    validation_score: Optional[Any] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stages: List[StageResponse] = []
    artifacts: List[ArtifactResponse] = []
    opportunity: Optional[dict] = None

    class Config:
        from_attributes = True


class EnhancedWorkspaceList(BaseModel):
    workspaces: List[EnhancedWorkspaceResponse]
    total: int


class TaskComplete(BaseModel):
    is_completed: bool = True


class TaskCreate(BaseModel):
    stage_id: int
    title: str
    description: Optional[str] = None


class AIInsightRequest(BaseModel):
    insight_type: str = Field(..., description="Type: summary, recommendations, validation_score, interview_guide, survey_questions, competitor_analysis, financial_model")
    context: Optional[dict] = None


class AIInsightResponse(BaseModel):
    insight_type: str
    content: Any
    confidence: Optional[float] = None
    generated_at: datetime


class AnalyticsResponse(BaseModel):
    workspace_id: int
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    total_artifacts: int
    artifacts_by_type: dict
    stage_progress: List[dict]
    validation_score: Optional[Any] = None
    activity_timeline: List[dict] = []
    ai_recommendations: Optional[Any] = None
