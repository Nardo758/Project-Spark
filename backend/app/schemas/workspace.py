from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class WorkspaceStatusEnum(str, Enum):
    RESEARCHING = "researching"
    VALIDATING = "validating"
    PLANNING = "planning"
    BUILDING = "building"
    LAUNCHED = "launched"
    PAUSED = "paused"
    ARCHIVED = "archived"


class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class WorkspaceNoteBase(BaseModel):
    title: Optional[str] = None
    content: str
    is_pinned: bool = False


class WorkspaceNoteCreate(WorkspaceNoteBase):
    pass


class WorkspaceNoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None


class WorkspaceNote(WorkspaceNoteBase):
    id: int
    workspace_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkspaceTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    due_date: Optional[datetime] = None


class WorkspaceTaskCreate(WorkspaceTaskBase):
    pass


class WorkspaceTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[TaskPriorityEnum] = None
    due_date: Optional[datetime] = None
    sort_order: Optional[int] = None


class WorkspaceTask(WorkspaceTaskBase):
    id: int
    workspace_id: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    sort_order: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkspaceDocumentBase(BaseModel):
    name: str
    doc_type: Optional[str] = None
    content: Optional[str] = None
    file_url: Optional[str] = None


class WorkspaceDocumentCreate(WorkspaceDocumentBase):
    pass


class WorkspaceDocument(WorkspaceDocumentBase):
    id: int
    workspace_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkspaceCreate(BaseModel):
    opportunity_id: int
    custom_title: Optional[str] = None
    description: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    status: Optional[WorkspaceStatusEnum] = None
    progress_percent: Optional[int] = None
    custom_title: Optional[str] = None
    description: Optional[str] = None
    ai_context: Optional[str] = None


class OpportunitySummary(BaseModel):
    id: int
    title: str
    category: str
    description: Optional[str] = None
    feasibility_score: Optional[float] = None

    class Config:
        from_attributes = True


class Workspace(BaseModel):
    id: int
    user_id: int
    opportunity_id: int
    status: WorkspaceStatusEnum
    progress_percent: int
    custom_title: Optional[str] = None
    description: Optional[str] = None
    ai_context: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    
    opportunity: Optional[OpportunitySummary] = None
    notes: List[WorkspaceNote] = []
    tasks: List[WorkspaceTask] = []
    documents: List[WorkspaceDocument] = []

    class Config:
        from_attributes = True


class WorkspaceList(BaseModel):
    workspaces: List[Workspace]
    total: int


class WorkspaceCheck(BaseModel):
    has_workspace: bool
    workspace_id: Optional[int] = None
