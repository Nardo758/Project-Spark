from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class LifecycleStateEnum(str, Enum):
    DISCOVERED = "discovered"
    SAVED = "saved"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    LAUNCHED = "launched"
    PAUSED = "paused"
    ARCHIVED = "archived"


class TagSchema(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


class OpportunityInWatchlist(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    market_size: Optional[str] = None
    ai_competition_level: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WatchlistItemCreate(BaseModel):
    """Schema for creating a watchlist item"""
    opportunity_id: int


class WatchlistItem(BaseModel):
    """Schema for watchlist item response"""
    id: int
    user_id: int
    opportunity_id: int
    collection_id: Optional[int] = None
    lifecycle_state: LifecycleStateEnum = LifecycleStateEnum.SAVED
    state_changed_at: Optional[datetime] = None
    paused_reason: Optional[str] = None
    archived_reason: Optional[str] = None
    created_at: datetime
    opportunity: Optional[OpportunityInWatchlist] = None
    tags: List[TagSchema] = []

    class Config:
        from_attributes = True


class LifecycleTransitionRequest(BaseModel):
    """Request to transition lifecycle state"""
    new_state: LifecycleStateEnum
    reason: Optional[str] = None


class LifecycleTransitionResponse(BaseModel):
    """Response from lifecycle state transition"""
    id: int
    previous_state: LifecycleStateEnum
    new_state: LifecycleStateEnum
    state_changed_at: datetime
    allowed_transitions: List[LifecycleStateEnum]


LIFECYCLE_STATE_INFO = {
    LifecycleStateEnum.DISCOVERED: {
        "label": "Discovered",
        "description": "Browse, preview, unlock",
        "color": "#6b7280",
        "icon": "search",
        "step": 1
    },
    LifecycleStateEnum.SAVED: {
        "label": "Saved",
        "description": "Organize, tag, notes, collections",
        "color": "#3b82f6",
        "icon": "bookmark",
        "step": 2
    },
    LifecycleStateEnum.ANALYZING: {
        "label": "Analyzing",
        "description": "Market research, AI assistant",
        "color": "#8b5cf6",
        "icon": "chart-bar",
        "step": 3
    },
    LifecycleStateEnum.PLANNING: {
        "label": "Planning",
        "description": "Business plan, strategy",
        "color": "#f59e0b",
        "icon": "clipboard-list",
        "step": 4
    },
    LifecycleStateEnum.EXECUTING: {
        "label": "Executing",
        "description": "Building, team, funding",
        "color": "#10b981",
        "icon": "play",
        "step": 5
    },
    LifecycleStateEnum.LAUNCHED: {
        "label": "Launched",
        "description": "Live business, tracking",
        "color": "#22c55e",
        "icon": "rocket",
        "step": 6
    },
    LifecycleStateEnum.PAUSED: {
        "label": "Paused",
        "description": "On hold, monitoring",
        "color": "#f97316",
        "icon": "pause",
        "step": 0
    },
    LifecycleStateEnum.ARCHIVED: {
        "label": "Archived",
        "description": "Completed or closed",
        "color": "#9ca3af",
        "icon": "archive",
        "step": 0
    },
}
