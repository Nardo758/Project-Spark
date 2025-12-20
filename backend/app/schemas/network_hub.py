from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConnectionRequestCreate(BaseModel):
    target_user_id: int
    message: Optional[str] = None
    context_type: Optional[str] = None
    context_id: Optional[str] = None


class ConnectionRequestOut(BaseModel):
    id: int
    requester_id: int
    target_user_id: int
    status: str
    message: Optional[str] = None
    context_type: Optional[str] = None
    context_id: Optional[str] = None
    created_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ThreadOut(BaseModel):
    id: int
    thread_type: str
    user_a_id: int
    user_b_id: int
    context_type: Optional[str] = None
    context_id: Optional[str] = None
    created_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class MessageOut(BaseModel):
    id: int
    thread_id: int
    sender_id: int
    body: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

