from pydantic import BaseModel
from datetime import datetime


class ValidationBase(BaseModel):
    opportunity_id: int


class ValidationCreate(ValidationBase):
    pass


class Validation(ValidationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
