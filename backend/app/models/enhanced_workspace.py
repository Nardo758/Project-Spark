# 🚀 ENHANCED WORKSPACE MODELS
# Production-ready database models for OppGrid

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum as SAEnum, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum
from datetime import datetime

class WorkflowStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"

class WorkflowType(str, enum.Enum):
    LEAN_VALIDATION = "lean_validation"
    ENTERPRISE_B2B = "enterprise_b2b"
    PRODUCT_MARKET_FIT = "product_market_fit"
    CUSTOM = "custom"

class ResearchArtifactType(str, enum.Enum):
    INTERVIEW = "interview"
    SURVEY = "survey"
    DOCUMENT = "document"
    ANALYSIS = "analysis"
    PROTOTYPE = "prototype"
    COMPETITOR = "competitor"
    FINANCIAL = "financial"
    MARKET = "market"

class ResearchArtifactStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# Enhanced workspace models
class EnhancedUserWorkspace(Base):
    __tablename__ = "enhanced_user_workspaces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Enhanced project information
    custom_title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    ai_context = Column(Text, nullable=True)
    
    # Enhanced workflow system
    workflow_type = Column(SAEnum(WorkflowType), default=WorkflowType.CUSTOM, nullable=False)
    workflow_config = Column(JSON, nullable=True)  # Custom workflow configuration
    current_stage = Column(String(100), nullable=True)
    current_phase = Column(String(100), nullable=True)
    
    # Progress tracking
    progress_percent = Column(Integer, default=0)
    stage_progress = Column(JSON, nullable=True)  # Progress by stage
    
    # Enhanced workspace AI context
    ai_research_context = Column(JSON, nullable=True)  # AI-generated research context
    ai_recommendations = Column(JSON, nullable=True)  # AI recommendations by stage
    
    # Research data aggregation
    research_summary = Column(JSON, nullable=True)  # Aggregated research data
    validation_score = Column(JSON, nullable=True)  # Validation score by category
    
    # Enhanced status tracking
    status = Column(SAEnum(WorkflowStatus), default=WorkflowStatus.NOT_STARTED, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="enhanced_workspaces")
    opportunity = relationship("Opportunity", back_populates="enhanced_workspaces")
    workflow_stages = relationship("EnhancedWorkflowStage", back_populates="workspace", cascade="all, delete-orphan")
    research_artifacts = relationship("EnhancedResearchArtifact", back_populates="workspace", cascade="all, delete-orphan")
    workspace_chat = relationship("EnhancedWorkspaceChat", back_populates="workspace", cascade="all, delete-orphan")
    custom_workflows = relationship("CustomWorkflow", back_populates="workspace", cascade="all, delete-orphan")


class EnhancedWorkflowStage(Base):
    __tablename__ = "enhanced_workflow_stages"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("enhanced_user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    duration_weeks = Column(Integer, nullable=True)
    
    status = Column(SAEnum(WorkflowStatus), default=WorkflowStatus.NOT_STARTED, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Enhanced stage configuration
    stage_config = Column(JSON, nullable=True)  # Stage-specific configuration
    ai_recommendations = Column(JSON, nullable=True)  # AI recommendations for this stage
    research_summary = Column(JSON, nullable=True)  # Research summary for this stage
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    workspace = relationship("EnhancedUserWorkspace", back_populates="workflow_stages")
    tasks = relationship("EnhancedWorkflowTask", back_populates="stage", cascade="all, delete-orphan")
    research_artifacts = relationship("EnhancedResearchArtifact", back_populates="stage", cascade="all, delete-orphan")


class EnhancedWorkflowTask(Base):
    __tablename__ = "enhanced_workflow_tasks"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("enhanced_workflow_stages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    priority = Column(String(50), default="todo")
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    sort_order = Column(Integer, default=0)
    
    # Enhanced task configuration
    task_config = Column(JSON, nullable=True)  # Task-specific configuration
    ai_assistance_requested = Column(Boolean, default=False)
    ai_assistance_completed = Column(Boolean, default=False)
    ai_assistance_result = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    stage = relationship("EnhancedWorkflowStage", back_populates="tasks")


class EnhancedResearchArtifact(Base):
    __tablename__ = "enhanced_research_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("enhanced_user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    stage_id = Column(Integer, ForeignKey("enhanced_workflow_stages.id", ondelete="CASCADE"), nullable=True, index=True)
    
    name = Column(String(255), nullable=False)
    artifact_type = Column(SAEnum(ResearchArtifactType), nullable=False)
    status = Column(SAEnum(ResearchArtifactStatus), default=ResearchArtifactStatus.DRAFT, nullable=False)
    
    # Enhanced artifact content and metadata
    content = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=True)
    metadata = Column(JSON, nullable=True)  # Enhanced metadata
    tags = Column(ARRAY(String), nullable=True)  # PostgreSQL array for tags
    
    # AI-generated insights and analysis
    ai_insights = Column(JSON, nullable=True)  # AI-generated insights
    ai_summary = Column(Text, nullable=True)  # AI-generated summary
    ai_recommendations = Column(JSON, nullable=True)  # AI recommendations
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    workspace = relationship("EnhancedUserWorkspace", back_populates="research_artifacts")
    stage = relationship("EnhancedWorkflowStage", back_populates="research_artifacts")


class EnhancedWorkspaceChat(Base):
    __tablename__ = "enhanced_workspace_chat"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("enhanced_user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)  # Enhanced metadata for AI responses
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    workspace = relationship("EnhancedUserWorkspace", back_populates="workspace_chat")


class CustomWorkflow(Base):
    __tablename__ = "custom_workflows"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("enhanced_user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    workflow_type = Column(SAEnum(WorkflowType), default=WorkflowType.CUSTOM, nullable=False)
    
    # Custom workflow configuration
    workflow_config = Column(JSON, nullable=False)  # Complete workflow configuration
    workflow_stages = Column(JSON, nullable=True)  # Stage definitions
    workflow_tasks = Column(JSON, nullable=True)  # Task definitions
    workflow_tools = Column(JSON, nullable=True)  # Tool definitions
    
    # Workflow statistics and metrics
    usage_count = Column(Integer, default=0)
    average_completion_time = Column(Integer, nullable=True)  # Average completion time in days
    success_rate = Column(Integer, nullable=True)  # Success rate percentage
    
    is_public = Column(Boolean, default=False)  # Can be shared with community
    is_featured = Column(Boolean, default=False)  # Featured in marketplace
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    workspace = relationship("EnhancedUserWorkspace", back_populates="custom_workflows")
    creator = relationship("User", back_populates="custom_workflows")