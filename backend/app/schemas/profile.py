from pydantic import BaseModel, Field
from typing import Optional, List, Any
from decimal import Decimal


class UserProfileBase(BaseModel):
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    risk_tolerance: Optional[int] = Field(default=None, ge=0, le=100)
    available_capital: Optional[Decimal] = None
    time_commitment_hours_per_week: Optional[int] = Field(default=None, ge=0, le=168)
    past_successes: Optional[Any] = None
    failure_patterns: Optional[Any] = None
    learning_style: Optional[str] = None


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

