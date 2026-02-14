from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.models.enhanced_workspace import ArtifactType, WorkflowType
from app.core.dependencies import get_current_active_user
from app.services.enhanced_workspace_service import EnhancedWorkspaceService, WORKFLOW_TEMPLATES
from app.schemas.enhanced_workspace import (
    EnhancedWorkspaceCreate, EnhancedWorkspaceUpdate,
    EnhancedWorkspaceResponse, EnhancedWorkspaceList,
    ArtifactCreate, ArtifactResponse,
    TaskCreate, TaskComplete, TaskResponse,
    AIInsightRequest, AIInsightResponse,
    AnalyticsResponse,
)

router = APIRouter()


def _workspace_to_response(ws) -> dict:
    opp = ws.opportunity
    opp_dict = None
    if opp:
        opp_dict = {
            "id": opp.id,
            "title": opp.title,
            "category": opp.category,
            "description": opp.description,
            "feasibility_score": getattr(opp, 'feasibility_score', None),
        }

    return {
        "id": ws.id,
        "user_id": ws.user_id,
        "opportunity_id": ws.opportunity_id,
        "workspace_id": ws.workspace_id,
        "custom_title": ws.custom_title,
        "description": ws.description,
        "ai_context": ws.ai_context,
        "workflow_type": ws.workflow_type.value if hasattr(ws.workflow_type, 'value') else ws.workflow_type,
        "current_stage": ws.current_stage,
        "current_phase": ws.current_phase,
        "progress_percent": ws.progress_percent or 0,
        "stage_progress": ws.stage_progress,
        "ai_research_context": ws.ai_research_context,
        "ai_recommendations": ws.ai_recommendations,
        "research_summary": ws.research_summary,
        "validation_score": ws.validation_score,
        "status": ws.status.value if hasattr(ws.status, 'value') else ws.status,
        "started_at": ws.started_at,
        "completed_at": ws.completed_at,
        "last_activity_at": ws.last_activity_at,
        "created_at": ws.created_at,
        "updated_at": ws.updated_at,
        "stages": [
            {
                "id": s.id,
                "workspace_id": s.workspace_id,
                "name": s.name,
                "description": s.description,
                "stage_order": s.stage_order,
                "status": s.status.value if hasattr(s.status, 'value') else s.status,
                "progress_percent": s.progress_percent or 0,
                "started_at": s.started_at,
                "completed_at": s.completed_at,
                "tasks": [
                    {
                        "id": t.id,
                        "stage_id": t.stage_id,
                        "workspace_id": t.workspace_id,
                        "title": t.title,
                        "description": t.description,
                        "is_completed": t.is_completed,
                        "sort_order": t.sort_order,
                        "ai_suggestion": t.ai_suggestion,
                        "completed_at": t.completed_at,
                        "created_at": t.created_at,
                    } for t in (s.tasks or [])
                ],
            } for s in (ws.stages or [])
        ],
        "artifacts": [
            {
                "id": a.id,
                "workspace_id": a.workspace_id,
                "artifact_type": a.artifact_type.value if hasattr(a.artifact_type, 'value') else a.artifact_type,
                "title": a.title,
                "content": a.content,
                "summary": a.summary,
                "ai_analysis": a.ai_analysis,
                "tags": a.tags,
                "source": a.source,
                "confidence_score": a.confidence_score,
                "created_at": a.created_at,
                "updated_at": a.updated_at,
            } for a in (ws.artifacts or [])
        ],
        "opportunity": opp_dict,
    }


@router.get("/enhanced-workspaces", response_model=EnhancedWorkspaceList)
def list_enhanced_workspaces(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    workspaces, total = service.list_workspaces(current_user.id, skip, limit)
    return {
        "workspaces": [_workspace_to_response(ws) for ws in workspaces],
        "total": total,
    }


@router.post("/enhanced-workspaces", response_model=EnhancedWorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_enhanced_workspace(
    data: EnhancedWorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    try:
        wt = WorkflowType(data.workflow_type.value)
    except ValueError:
        wt = WorkflowType.LEAN_VALIDATION

    try:
        workspace = service.create_workspace(
            user_id=current_user.id,
            opportunity_id=data.opportunity_id,
            workflow_type=wt,
            custom_title=data.custom_title,
            description=data.description,
            custom_stages=data.custom_stages,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return _workspace_to_response(service.get_workspace(workspace.id, current_user.id))


@router.get("/enhanced-workspaces/{workspace_id}", response_model=EnhancedWorkspaceResponse)
def get_enhanced_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    workspace = service.get_workspace(workspace_id, current_user.id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enhanced workspace not found")
    return _workspace_to_response(workspace)


@router.patch("/enhanced-workspaces/{workspace_id}", response_model=EnhancedWorkspaceResponse)
def update_enhanced_workspace(
    workspace_id: int,
    data: EnhancedWorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    updates = data.model_dump(exclude_none=True)
    if "status" in updates:
        updates["status"] = updates["status"]
    workspace = service.update_workspace(workspace_id, current_user.id, updates)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return _workspace_to_response(service.get_workspace(workspace_id, current_user.id))


@router.post("/enhanced-workspaces/{workspace_id}/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_enhanced_task(
    workspace_id: int,
    task_id: int,
    data: TaskComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    task = service.complete_task(workspace_id, task_id, current_user.id, data.is_completed)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/enhanced-workspaces/{workspace_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def add_enhanced_task(
    workspace_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    task = service.add_task(workspace_id, data.stage_id, current_user.id, data.title, data.description)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace or stage not found")
    return task


@router.post("/enhanced-workspaces/{workspace_id}/artifacts", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
def create_artifact(
    workspace_id: int,
    data: ArtifactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    try:
        at = ArtifactType(data.artifact_type.value)
    except ValueError:
        at = ArtifactType.CUSTOM

    artifact = service.create_artifact(
        workspace_id=workspace_id,
        user_id=current_user.id,
        artifact_type=at,
        title=data.title,
        content=data.content,
        summary=data.summary,
        tags=data.tags,
        source=data.source,
    )
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return artifact


@router.delete("/enhanced-workspaces/{workspace_id}/artifacts/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artifact(
    workspace_id: int,
    artifact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    if not service.delete_artifact(workspace_id, artifact_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")


@router.post("/enhanced-workspaces/{workspace_id}/ai/insights", response_model=AIInsightResponse)
def generate_ai_insight(
    workspace_id: int,
    data: AIInsightRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    result = service.generate_ai_insight(workspace_id, current_user.id, data.insight_type, data.context)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return {
        "insight_type": result["insight_type"],
        "content": result["content"],
        "confidence": result.get("confidence"),
        "generated_at": result.get("generated_at", datetime.utcnow()),
    }


@router.get("/enhanced-workspaces/{workspace_id}/analytics", response_model=AnalyticsResponse)
def get_workspace_analytics(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EnhancedWorkspaceService(db)
    analytics = service.get_analytics(workspace_id, current_user.id)
    if not analytics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return analytics


@router.get("/enhanced-workspaces/workflow-templates")
def get_workflow_templates():
    templates = []
    for wtype, template in WORKFLOW_TEMPLATES.items():
        templates.append({
            "type": wtype.value,
            "name": template["name"],
            "stages": [{"name": s["name"], "description": s.get("description", ""), "task_count": len(s.get("tasks", []))} for s in template["stages"]],
            "total_tasks": sum(len(s.get("tasks", [])) for s in template["stages"]),
        })
    return {"templates": templates}
