from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    content: str
    opportunity_id: int


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: str


class Comment(CommentBase):
    id: int
    user_id: int
    likes: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
