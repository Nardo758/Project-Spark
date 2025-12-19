from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict


class TrackingEventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    path: Optional[str] = Field(default=None, max_length=500)
    referrer: Optional[str] = Field(default=None, max_length=500)
    anonymous_id: Optional[str] = Field(default=None, max_length=64)
    properties: Optional[Dict[str, Any]] = None


class TrackingEventOut(BaseModel):
    id: int
    name: str
    path: Optional[str] = None
    referrer: Optional[str] = None
    user_id: Optional[int] = None
    anonymous_id: Optional[str] = None
    properties: Optional[dict] = None
    created_at: Any

    class Config:
        from_attributes = True

