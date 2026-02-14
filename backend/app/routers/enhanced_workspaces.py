# 🚀 ENHANCED WORKSPACE API ROUTER
# Production-ready API endpoints for OppGrid enhanced workspace

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.db.database import get_db
from app.models.enhanced_workspace import (
    EnhancedUserWorkspace, EnhancedWorkflowStage, EnhancedWorkflowTask,
    EnhancedResearchArtifact, CustomWorkflow, WorkflowType, WorkflowStatus,
    ResearchArtifactType, ResearchArtifactStatus
)
from app.models.user import User
from app.models.opportunity import Opportunity
from app.core.dependencies import get_current_active_user
from app.services.enhanced_workspace_service import EnhancedWorkspaceService

router = APIRouter(prefix="/enhanced-workspaces", tags=["enhanced-workspaces"])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_enhanced_workspace(
    opportunity_id: int,
    workflow_type: WorkflowType = WorkflowType.CUSTOM,
    custom_title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create enhanced workspace with custom workflow"""
    
    # Verify opportunity exists
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Check if workspace already exists
    existing_workspace = db.query(EnhancedUserWorkspace).filter(
        EnhancedUserWorkspace.user_id == current_user.id,
        EnhancedUserWorkspace.opportunity_id == opportunity_id
    ).first()
    
    if existing_workspace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enhanced workspace already exists for this opportunity"
        )
    
    service = EnhancedWorkspaceService(db)
    workspace = service.create_enhanced_workspace(
        user_id=current_user.id,
        opportunity_id=opportunity_id,
        workflow_type=workflow_type,
        custom_title=custom_title
    )
    
    return {
        "id": workspace.id,
        "workflow_type": workspace.workflow_type,
        "status": workspace.status,
        "progress_percent": workspace.progress_percent,
        "stages_count": len(workspace.workflow_stages),
        "message": "Enhanced workspace created successfully"
    }

@router.get("/", response_model=List[dict])
def list_enhanced_workspaces(
    skip: int = 0,
    limit: int = 100,
    workflow_type: Optional[WorkflowType] = None,
    status: Optional[WorkflowStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List user's enhanced workspaces"""
    
    query = db.query(EnhancedUserWorkspace).filter(
        EnhancedUserWorkspace.user_id == current_user.id
    )
    
    if workflow_type:
        query = query.filter(EnhancedUserWorkspace.workflow_type == workflow_type)
    
    if status:
        query = query.filter(EnhancedUserWorkspace.status == status)
    
    workspaces = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": workspace.id,
            "custom_title": workspace.custom_title,
            "workflow_type": workspace.workflow_type,
            "status": workspace.status,
            "progress_percent": workspace.progress_percent,
            "validation_score": workspace.validation_score,
            "research_summary": workspace.research_summary,
            "opportunity_title": workspace.opportunity.title if workspace.opportunity else None,
            "created_at": workspace.created_at,
            "last_activity_at": workspace.last_activity_at
        } for workspace in workspaces
    ]

@router.get("/{workspace_id}", response_model=dict)
def get_enhanced_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get enhanced workspace with all details"""
    
    workspace = db.query(EnhancedUserWorkspace).options(
        joinedload(EnhancedUserWorkspace.opportunity),
        joinedload(EnhancedUserWorkspace.workflow_stages).joinedload(EnhancedWorkflowStage.tasks),
        joinedload(EnhancedUserWorkspace.research_artifacts),
        joinedload(EnhancedUserWorkspace.custom_workflows)
    ).filter(
        EnhancedUserWorkspace.id == workspace_id,
        EnhancedUserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    return {
        "id": workspace.id,
        "custom_title": workspace.custom_title,
        "description": workspace.description,
        "workflow_type": workspace.workflow_type,
        "status": workspace.status,
        "progress_percent": workspace.progress_percent,
        "validation_score": workspace.validation_score,
        "research_summary": workspace.research_summary,
        "ai_recommendations": workspace.ai_recommendations,
        "opportunity": {
            "id": workspace.opportunity.id,
            "title": workspace.opportunity.title,
            "description": workspace.opportunity.description,
            "category": workspace.opportunity.category,
            "ai_opportunity_score": workspace.opportunity.ai_opportunity_score,
            "validation_count": workspace.opportunity.validation_count,
            "feasibility_score": workspace.opportunity.feasibility_score
        },
        "stages": [
            {
                "id": stage.id,
                "name": stage.name,
                "description": stage.description,
                "order_index": stage.order_index,
                "duration_weeks": stage.duration_weeks,
                "status": stage.status,
                "started_at": stage.started_at,
                "completed_at": stage.completed_at,
                "ai_recommendations": stage.ai_recommendations,
                "tasks": [
                    {
                        "id": task.id,
                        "name": task.name,
                        "description": task.description,
                        "is_completed": task.is_completed,
                        "priority": task.priority,
                        "due_date": task.due_date,
                        "completed_at": task.completed_at,
                        "sort_order": task.sort_order,
                        "ai_assistance_requested": task.ai_assistance_requested,
                        "ai_assistance_completed": task.ai_assistance_completed
                    } for task in stage.tasks
                ]
            } for stage in workspace.workflow_stages
        ],
        "research_artifacts": [
            {
                "id": artifact.id,
                "name": artifact.name,
                "artifact_type": artifact.artifact_type,
                "status": artifact.status,
                "content": artifact.content,
                "file_url": artifact.file_url,
                "metadata": artifact.artifact_metadata,
                "tags": artifact.tags,
                "ai_insights": artifact.ai_insights,
                "ai_summary": artifact.ai_summary,
                "ai_recommendations": artifact.ai_recommendations,
                "created_at": artifact.created_at,
                "updated_at": artifact.updated_at
            } for artifact in workspace.research_artifacts
        ],
        "created_at": workspace.created_at,
        "updated_at": workspace.updated_at,
        "last_activity_at": workspace.last_activity_at
    }

@router.put("/{workspace_id}", response_model=dict)
def update_enhanced_workspace(
    workspace_id: int,
    custom_title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[WorkflowStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update enhanced workspace details"""
    
    workspace = db.query(EnhancedUserWorkspace).filter(
        EnhancedUserWorkspace.id == workspace_id,
        EnhancedUserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    if custom_title is not None:
        workspace.custom_title = custom_title
    
    if description is not None:
        workspace.description = description
    
    if status is not None:
        workspace.status = status
        if status == WorkflowStatus.IN_PROGRESS and not workspace.started_at:
            workspace.started_at = datetime.utcnow()
        elif status == WorkflowStatus.COMPLETED and not workspace.completed_at:
            workspace.completed_at = datetime.utcnow()
    
    workspace.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "id": workspace.id,
        "custom_title": workspace.custom_title,
        "description": workspace.description,
        "status": workspace.status,
        "updated_at": workspace.updated_at,
        "message": "Workspace updated successfully"
    }

@router.post("/{workspace_id}/artifacts", response_model=dict)
def create_research_artifact(
    workspace_id: int,
    name: str,
    artifact_type: ResearchArtifactType,
    stage_id: Optional[int] = None,
    content: Optional[str] = None,
    file_url: Optional[str] = None,
    tags: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create research artifact with AI insights"""
    
    # Verify workspace ownership
    workspace = db.query(EnhancedUserWorkspace).filter(
        EnhancedUserWorkspace.id == workspace_id,
        EnhancedUserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Verify stage if provided
    if stage_id:
        stage = db.query(EnhancedWorkflowStage).filter(
            EnhancedWorkflowStage.id == stage_id,
            EnhancedWorkflowStage.workspace_id == workspace_id
        ).first()
        
        if not stage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stage not found in workspace"
            )
    
    service = EnhancedWorkspaceService(db)
    artifact = service.create_research_artifact(
        workspace_id=workspace_id,
        stage_id=stage_id,
        name=name,
        artifact_type=artifact_type,
        content=content,
        file_url=file_url,
        artifact_metadata={"tags": tags} if tags else None
    )
    
    # Update workspace last activity
    workspace.last_activity_at = datetime.utcnow()
    db.commit()
    
    return {
        "id": artifact.id,
        "name": artifact.name,
        "artifact_type": artifact.artifact_type,
        "status": artifact.status,
        "ai_insights": artifact.ai_insights,
        "ai_summary": artifact.ai_summary,
        "ai_recommendations": artifact.ai_recommendations,
        "created_at": artifact.created_at
    }

@router.get("/{workspace_id}/artifacts", response_model=List[dict])
def list_research_artifacts(
    workspace_id: int,
    artifact_type: Optional[ResearchArtifactType] = None,
    stage_id: Optional[int] = None,
    status: Optional[ResearchArtifactStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List research artifacts for workspace"""
    
    # Verify workspace ownership
    workspace = db.query(EnhancedUserWorkspace).filter(
        EnhancedUserWorkspace.id == workspace_id,
        EnhancedUserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    query = db.query(EnhancedResearchArtifact).filter(
        EnhancedResearchArtifact.workspace_id == workspace_id
    )
    
    if artifact_type:
        query = query.filter(EnhancedResearchArtifact.artifact_type == artifact_type)
    
    if stage_id:
        query = query.filter(EnhancedResearchArtifact.stage_id == stage_id)
    
    if status:
        query = query.filter(EnhancedResearchArtifact.status == status)
    
    artifacts = query.order_by(EnhancedResearchArtifact.created_at.desc()).all()
    
    return [
        {
            "id": artifact.id,
            "name": artifact.name,
            "artifact_type": artifact.artifact_type,
            "status": artifact.status,
            "content": artifact.content,
            "file_url": artifact.file_url,
            "metadata": artifact.artifact_metadata,
            "tags": artifact.tags,
            "ai_insights": artifact.ai_insights,
            "ai_summary": artifact.ai_summary,
            "ai_recommendations": artifact.ai_recommendations,
            "stage_id": artifact.stage_id,
            "created_at": artifact.created_at,
            "updated_at": artifact.updated_at
        } for artifact in artifacts
    ]

@router.put("/{workspace_id}/tasks/{task_id}/complete", response_model=dict)
def complete_task(
    workspace_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Complete task and update workspace progress"""
    
    # Verify workspace ownership
    workspace = db.query(EnhancedUserWorkspace).filter(
        EnhancedUserWorkspace.id == workspace_id,
        EnhancedUserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Find and complete task
    task = db.query(EnhancedWorkflowTask).join(EnhancedWorkflowStage).filter(
        EnhancedWorkflowTask.id == task_id,
        EnhancedWorkflowStage.workspace_id == workspace_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.is_completed = True
    task.completed_at = datetime.utcnow()
    task.priority = "done"
    
    # Update workspace progress
    service = EnhancedWorkspaceService(db)
    progress_update = service.update_workspace_progress(workspace_id)
    
    # Update workspace last activity
    workspace.last_activity_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "task_completed": True,
        "progress_update": progress_update,
        "message": "Task completed successfully"
    }

@router.get("/{workspace_id}/analytics", response_model=dict)
def get_workspace_analytics(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive workspace analytics"""
    
    workspace = db.query(EnhancedUserWorkspace).filter(
        EnhancedUserWorkspace.id == workspace_id,
        EnhancedUserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    service = EnhancedWorkspaceService(db)
    analytics = service.get_workspace_analytics(workspace_id)
    
    return analytics

@router.post("/{workspace_id}/custom-workflows", response_model=dict)
def create_custom_workflow(
    workspace_id: int,
    name: str,
    description: Optional[str] = None,
    workflow_config: Dict[str, Any] = None,
    is_public: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create custom workflow template"""
    
    # Verify workspace ownership
    workspace = db.query(EnhancedUserWorkspace).filter(
        EnhancedUserWorkspace.id == workspace_id,
        EnhancedUserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    custom_workflow = CustomWorkflow(
        workspace_id=workspace_id,
        created_by=current_user.id,
        name=name,
        description=description,
        workflow_config=workflow_config or {},
        is_public=is_public
    )
    
    db.add(custom_workflow)
    db.commit()
    
    return {
        "id": custom_workflow.id,
        "name": custom_workflow.name,
        "description": custom_workflow.description,
        "is_public": custom_workflow.is_public,
        "created_at": custom_workflow.created_at,
        "message": "Custom workflow created successfully"
    }

@router.get("/custom-workflows/public", response_model=List[dict])
def get_public_custom_workflows(
    skip: int = 0,
    limit: int = 50,
    workflow_type: Optional[WorkflowType] = None,
    db: Session = Depends(get_db)
):
    """Get public custom workflows (community marketplace)"""
    
    query = db.query(CustomWorkflow).filter(
        CustomWorkflow.is_public == True
    )
    
    if workflow_type:
        query = query.filter(CustomWorkflow.workflow_type == workflow_type)
    
    workflows = query.order_by(CustomWorkflow.usage_count.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "workflow_type": workflow.workflow_type,
            "usage_count": workflow.usage_count,
            "success_rate": workflow.success_rate,
            "created_by": {
                "id": workflow.creator.id,
                "username": workflow.creator.username,
                "avatar_url": workflow.creator.avatar_url
            },
            "created_at": workflow.created_at
        } for workflow in workflows
    ]