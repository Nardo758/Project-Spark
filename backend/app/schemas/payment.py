from pydantic import BaseModel, Field
from typing import Optional, Any


class CreateMicroPaymentIntentRequest(BaseModel):
    amount_cents: int = Field(..., ge=50, le=500000)  # $0.50 - $5000
    expert_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    purpose: str = Field(default="expert_micro_task", min_length=1, max_length=100)
    metadata: Optional[Any] = None


class CreateProjectPaymentIntentRequest(BaseModel):
    amount_cents: int = Field(..., ge=10000, le=5000000)  # $100 - $50k
    expert_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    purpose: str = Field(default="expert_project", min_length=1, max_length=100)
    metadata: Optional[Any] = None


class CreatePaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    transaction_id: int


class ConfirmPaymentRequest(BaseModel):
    payment_intent_id: str


class ConfirmPaymentResponse(BaseModel):
    success: bool
    status: str
    transaction_id: Optional[int] = None

