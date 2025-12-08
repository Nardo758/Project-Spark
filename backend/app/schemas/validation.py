from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ValidationBase(BaseModel):
    opportunity_id: int
    is_valid: bool
    comment: Optional[str] = None


class ValidationCreate(ValidationBase):
    pass


class Validation(ValidationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
