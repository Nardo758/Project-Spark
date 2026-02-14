from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum as SAEnum, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class WorkflowType(str, enum.Enum):
    LEAN_VALIDATION = "lean_validation"
    ENTERPRISE_B2B = "enterprise_b2b"
    PRODUCT_MARKET_FIT = "product_market_fit"
    CUSTOM = "custom"


class EnhancedWorkflowStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class ArtifactType(str, enum.Enum):
    INTERVIEW = "interview"
    SURVEY = "survey"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    FINANCIAL_MODEL = "financial_model"
    MARKET_RESEARCH = "market_research"
    CUSTOMER_PERSONA = "customer_persona"
    SWOT_ANALYSIS = "swot_analysis"
    NOTES = "notes"
    AI_INSIGHT = "ai_insight"
    CUSTOM = "custom"


WORKFLOW_TEMPLATES = {
    WorkflowType.LEAN_VALIDATION: {
        "name": "Lean Validation",
        "stages": [
            {"name": "Problem Discovery", "order": 1, "description": "Identify and validate the core problem", "tasks": [
                "Define problem hypothesis", "Conduct 5 customer interviews", "Map pain points and frequency", "Validate problem-solution fit"
            ]},
            {"name": "Market Analysis", "order": 2, "description": "Analyze market size and dynamics", "tasks": [
                "Estimate TAM/SAM/SOM", "Identify market trends", "Analyze regulatory landscape", "Map value chain"
            ]},
            {"name": "Customer Validation", "order": 3, "description": "Validate with target customers", "tasks": [
                "Create customer survey", "Build landing page MVP", "Run smoke test ads", "Collect 50+ responses"
            ]},
            {"name": "Solution Design", "order": 4, "description": "Design the minimum viable solution", "tasks": [
                "Define MVP feature set", "Create wireframes/mockups", "Build financial projections", "Prepare pitch deck"
            ]},
        ]
    },
    WorkflowType.ENTERPRISE_B2B: {
        "name": "Enterprise B2B",
        "stages": [
            {"name": "Market Research", "order": 1, "description": "Deep dive into enterprise market", "tasks": [
                "Map industry landscape", "Identify decision makers", "Analyze procurement cycles", "Research compliance requirements"
            ]},
            {"name": "Stakeholder Mapping", "order": 2, "description": "Map key stakeholders and influencers", "tasks": [
                "Identify buyer personas", "Map organizational chart", "Analyze decision processes", "Find champion profiles"
            ]},
            {"name": "Decision Analysis", "order": 3, "description": "Understand buying decisions", "tasks": [
                "Analyze competitive alternatives", "Map budget allocation", "Identify switching costs", "Build ROI calculator"
            ]},
            {"name": "Go-to-Market", "order": 4, "description": "Plan enterprise GTM strategy", "tasks": [
                "Define pricing strategy", "Plan pilot program", "Create sales playbook", "Build partnership strategy"
            ]},
        ]
    },
    WorkflowType.PRODUCT_MARKET_FIT: {
        "name": "Product-Market Fit",
        "stages": [
            {"name": "Market Segmentation", "order": 1, "description": "Segment and prioritize markets", "tasks": [
                "Define market segments", "Score segment attractiveness", "Select beachhead market", "Profile ideal customer"
            ]},
            {"name": "Value Proposition", "order": 2, "description": "Craft and test value propositions", "tasks": [
                "Map jobs-to-be-done", "Define unique value proposition", "Test messaging with prospects", "A/B test positioning"
            ]},
            {"name": "MVP Testing", "order": 3, "description": "Build and test minimum viable product", "tasks": [
                "Define core features", "Build prototype", "Run beta program", "Measure engagement metrics"
            ]},
            {"name": "Scale Validation", "order": 4, "description": "Validate readiness to scale", "tasks": [
                "Measure retention/churn", "Calculate unit economics", "Test acquisition channels", "Build growth model"
            ]},
        ]
    },
}


class EnhancedUserWorkspace(Base):
    __tablename__ = "enhanced_user_workspaces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="SET NULL"), nullable=True, index=True)

    custom_title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    ai_context = Column(Text, nullable=True)

    workflow_type = Column(SAEnum(WorkflowType), default=WorkflowType.LEAN_VALIDATION, nullable=False)
    workflow_config = Column(JSON, nullable=True)
    current_stage = Column(String(100), nullable=True)
    current_phase = Column(String(100), nullable=True)
    progress_percent = Column(Integer, default=0)
    stage_progress = Column(JSON, nullable=True)

    ai_research_context = Column(JSON, nullable=True)
    ai_recommendations = Column(JSON, nullable=True)
    research_summary = Column(JSON, nullable=True)
    validation_score = Column(JSON, nullable=True)

    status = Column(SAEnum(EnhancedWorkflowStatus), default=EnhancedWorkflowStatus.NOT_STARTED, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    opportunity = relationship("Opportunity")
    base_workspace = relationship("UserWorkspace")
    stages = relationship("EnhancedWorkflowStage", back_populates="workspace", cascade="all, delete-orphan", order_by="EnhancedWorkflowStage.stage_order")
    artifacts = relationship("EnhancedResearchArtifact", back_populates="workspace", cascade="all, delete-orphan")


class EnhancedWorkflowStage(Base):
    __tablename__ = "enhanced_workflow_stages"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("enhanced_user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    stage_order = Column(Integer, default=0)
    status = Column(SAEnum(EnhancedWorkflowStatus), default=EnhancedWorkflowStatus.NOT_STARTED, nullable=False)
    progress_percent = Column(Integer, default=0)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("EnhancedUserWorkspace", back_populates="stages")
    tasks = relationship("EnhancedWorkflowTask", back_populates="stage", cascade="all, delete-orphan", order_by="EnhancedWorkflowTask.sort_order")


class EnhancedWorkflowTask(Base):
    __tablename__ = "enhanced_workflow_tasks"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("enhanced_workflow_stages.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(Integer, ForeignKey("enhanced_user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    ai_suggestion = Column(Text, nullable=True)

    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stage = relationship("EnhancedWorkflowStage", back_populates="tasks")
    workspace = relationship("EnhancedUserWorkspace")


class EnhancedResearchArtifact(Base):
    __tablename__ = "enhanced_research_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("enhanced_user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)

    artifact_type = Column(SAEnum(ArtifactType), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    source = Column(String(255), nullable=True)
    confidence_score = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("EnhancedUserWorkspace", back_populates="artifacts")
