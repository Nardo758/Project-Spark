"""
Pydantic schemas for Idea Validation product records.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class IdeaValidationCreatePaymentIntentRequest(BaseModel):
    idea: str
    title: str
    category: str
    amount_cents: int = 999


class IdeaValidationCreatePaymentIntentResponse(BaseModel):
    idea_validation_id: int
    client_secret: str
    payment_intent_id: str
    amount_cents: int
    currency: str = "usd"


class IdeaValidationRunRequest(BaseModel):
    """Run the validation after payment succeeded."""
    payment_intent_id: str


class IdeaValidationItem(BaseModel):
    id: int
    user_id: int
    title: str
    category: str
    status: str
    stripe_payment_intent_id: Optional[str] = None
    amount_cents: Optional[int] = None
    currency: Optional[str] = None
    opportunity_score: Optional[int] = None
    summary: Optional[str] = None
    validation_confidence: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IdeaValidationDetail(IdeaValidationItem):
    idea: str
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None


class IdeaValidationList(BaseModel):
    items: list[IdeaValidationItem]
    total: int

