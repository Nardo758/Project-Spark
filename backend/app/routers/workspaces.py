from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.workspace import UserWorkspace, WorkspaceNote, WorkspaceTask, WorkspaceDocument, WorkspaceStatus, TaskPriority
from app.models.opportunity import Opportunity
from app.models.user import User
from app.models.watchlist import WatchlistItem, LifecycleState

WORKSPACE_TO_LIFECYCLE = {
    WorkspaceStatus.RESEARCHING: LifecycleState.ANALYZING,
    WorkspaceStatus.VALIDATING: LifecycleState.ANALYZING,
    WorkspaceStatus.PLANNING: LifecycleState.PLANNING,
    WorkspaceStatus.BUILDING: LifecycleState.EXECUTING,
    WorkspaceStatus.LAUNCHED: LifecycleState.LAUNCHED,
    WorkspaceStatus.PAUSED: LifecycleState.PAUSED,
    WorkspaceStatus.ARCHIVED: LifecycleState.ARCHIVED,
}
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, Workspace as WorkspaceSchema,
    WorkspaceNoteCreate, WorkspaceNoteUpdate, WorkspaceNote as WorkspaceNoteSchema,
    WorkspaceTaskCreate, WorkspaceTaskUpdate, WorkspaceTask as WorkspaceTaskSchema,
    WorkspaceDocumentCreate, WorkspaceDocument as WorkspaceDocumentSchema,
    WorkspaceList, WorkspaceCheck
)
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=WorkspaceSchema, status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace_data: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start working on an opportunity - creates a personal workspace"""
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == workspace_data.opportunity_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    existing = db.query(UserWorkspace).filter(
        UserWorkspace.user_id == current_user.id,
        UserWorkspace.opportunity_id == workspace_data.opportunity_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a workspace for this opportunity"
        )

    new_workspace = UserWorkspace(
        user_id=current_user.id,
        opportunity_id=workspace_data.opportunity_id,
        custom_title=workspace_data.custom_title or opportunity.title,
        description=workspace_data.description,
        status=WorkspaceStatus.RESEARCHING
    )

    default_tasks = [
        WorkspaceTask(title="Review opportunity details", priority=TaskPriority.HIGH, sort_order=0),
        WorkspaceTask(title="Validate market demand", priority=TaskPriority.HIGH, sort_order=1),
        WorkspaceTask(title="Analyze competition", priority=TaskPriority.MEDIUM, sort_order=2),
        WorkspaceTask(title="Identify target audience", priority=TaskPriority.MEDIUM, sort_order=3),
        WorkspaceTask(title="Create business model", priority=TaskPriority.MEDIUM, sort_order=4),
        WorkspaceTask(title="Connect with an expert", priority=TaskPriority.LOW, sort_order=5),
    ]
    new_workspace.tasks = default_tasks

    watchlist_item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.opportunity_id == workspace_data.opportunity_id
    ).first()
    if watchlist_item:
        watchlist_item.lifecycle_state = LifecycleState.ANALYZING
        watchlist_item.state_changed_at = func.now()

    db.add(new_workspace)
    db.commit()
    db.refresh(new_workspace)

    return new_workspace


@router.get("/", response_model=WorkspaceList)
def get_workspaces(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all user's workspaces"""
    query = db.query(UserWorkspace).filter(
        UserWorkspace.user_id == current_user.id
    ).options(
        joinedload(UserWorkspace.opportunity),
        joinedload(UserWorkspace.tasks),
        joinedload(UserWorkspace.notes)
    )

    if status_filter:
        try:
            ws_status = WorkspaceStatus(status_filter)
            query = query.filter(UserWorkspace.status == ws_status)
        except ValueError:
            pass

    total = query.count()
    workspaces = query.order_by(UserWorkspace.last_activity_at.desc()).offset(skip).limit(limit).all()

    return WorkspaceList(workspaces=workspaces, total=total)


@router.get("/check/{opportunity_id}", response_model=WorkspaceCheck)
def check_workspace(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if user has a workspace for an opportunity"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.opportunity_id == opportunity_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    return WorkspaceCheck(
        has_workspace=workspace is not None,
        workspace_id=workspace.id if workspace else None
    )


@router.get("/{workspace_id}", response_model=WorkspaceSchema)
def get_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific workspace with all details"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).options(
        joinedload(UserWorkspace.opportunity),
        joinedload(UserWorkspace.notes),
        joinedload(UserWorkspace.tasks),
        joinedload(UserWorkspace.documents)
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceSchema)
def update_workspace(
    workspace_id: int,
    update_data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update workspace status, progress, or details"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    update_dict = update_data.model_dump(exclude_unset=True)
    new_status = None
    for key, value in update_dict.items():
        if key == "status" and value:
            new_status = WorkspaceStatus(value)
            setattr(workspace, key, new_status)
        else:
            setattr(workspace, key, value)

    if new_status:
        lifecycle_state = WORKSPACE_TO_LIFECYCLE.get(new_status)
        if lifecycle_state:
            watchlist_item = db.query(WatchlistItem).filter(
                WatchlistItem.user_id == current_user.id,
                WatchlistItem.opportunity_id == workspace.opportunity_id
            ).first()
            if watchlist_item:
                watchlist_item.lifecycle_state = lifecycle_state
                watchlist_item.state_changed_at = func.now()
                if lifecycle_state not in [LifecycleState.PAUSED, LifecycleState.ARCHIVED]:
                    watchlist_item.paused_reason = None
                    watchlist_item.archived_reason = None

    workspace.last_activity_at = func.now()
    db.commit()
    db.refresh(workspace)

    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a workspace"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    db.delete(workspace)
    db.commit()

    return None


@router.post("/{workspace_id}/notes", response_model=WorkspaceNoteSchema, status_code=status.HTTP_201_CREATED)
def create_note(
    workspace_id: int,
    note_data: WorkspaceNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a note to workspace"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    note = WorkspaceNote(
        workspace_id=workspace_id,
        title=note_data.title,
        content=note_data.content,
        is_pinned=note_data.is_pinned
    )
    db.add(note)
    workspace.last_activity_at = func.now()
    db.commit()
    db.refresh(note)

    return note


@router.patch("/{workspace_id}/notes/{note_id}", response_model=WorkspaceNoteSchema)
def update_note(
    workspace_id: int,
    note_id: int,
    note_data: WorkspaceNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a note"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    note = db.query(WorkspaceNote).filter(
        WorkspaceNote.id == note_id,
        WorkspaceNote.workspace_id == workspace_id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_dict = note_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(note, key, value)

    workspace.last_activity_at = func.now()
    db.commit()
    db.refresh(note)

    return note


@router.delete("/{workspace_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    workspace_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a note"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    note = db.query(WorkspaceNote).filter(
        WorkspaceNote.id == note_id,
        WorkspaceNote.workspace_id == workspace_id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()

    return None


@router.post("/{workspace_id}/tasks", response_model=WorkspaceTaskSchema, status_code=status.HTTP_201_CREATED)
def create_task(
    workspace_id: int,
    task_data: WorkspaceTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a task to workspace"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    max_order = db.query(func.max(WorkspaceTask.sort_order)).filter(
        WorkspaceTask.workspace_id == workspace_id
    ).scalar() or 0

    task = WorkspaceTask(
        workspace_id=workspace_id,
        title=task_data.title,
        description=task_data.description,
        priority=TaskPriority(task_data.priority) if task_data.priority else TaskPriority.MEDIUM,
        due_date=task_data.due_date,
        sort_order=max_order + 1
    )
    db.add(task)
    workspace.last_activity_at = func.now()
    db.commit()
    db.refresh(task)

    return task


@router.patch("/{workspace_id}/tasks/{task_id}", response_model=WorkspaceTaskSchema)
def update_task(
    workspace_id: int,
    task_id: int,
    task_data: WorkspaceTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a task (including marking complete)"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    task = db.query(WorkspaceTask).filter(
        WorkspaceTask.id == task_id,
        WorkspaceTask.workspace_id == workspace_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_dict = task_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key == "priority" and value:
            setattr(task, key, TaskPriority(value))
        elif key == "is_completed":
            setattr(task, key, value)
            if value:
                task.completed_at = datetime.utcnow()
            else:
                task.completed_at = None
        else:
            setattr(task, key, value)

    total_tasks = db.query(WorkspaceTask).filter(WorkspaceTask.workspace_id == workspace_id).count()
    completed_tasks = db.query(WorkspaceTask).filter(
        WorkspaceTask.workspace_id == workspace_id,
        WorkspaceTask.is_completed == True
    ).count()
    if total_tasks > 0:
        workspace.progress_percent = int((completed_tasks / total_tasks) * 100)

    workspace.last_activity_at = func.now()
    db.commit()
    db.refresh(task)

    return task


@router.delete("/{workspace_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    workspace_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a task"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    task = db.query(WorkspaceTask).filter(
        WorkspaceTask.id == task_id,
        WorkspaceTask.workspace_id == workspace_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return None


@router.post("/{workspace_id}/documents", response_model=WorkspaceDocumentSchema, status_code=status.HTTP_201_CREATED)
def create_document(
    workspace_id: int,
    doc_data: WorkspaceDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a document to workspace"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    doc = WorkspaceDocument(
        workspace_id=workspace_id,
        name=doc_data.name,
        doc_type=doc_data.doc_type,
        content=doc_data.content,
        file_url=doc_data.file_url
    )
    db.add(doc)
    workspace.last_activity_at = func.now()
    db.commit()
    db.refresh(doc)

    return doc


@router.delete("/{workspace_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    workspace_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a document"""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    doc = db.query(WorkspaceDocument).filter(
        WorkspaceDocument.id == doc_id,
        WorkspaceDocument.workspace_id == workspace_id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()

    return None
