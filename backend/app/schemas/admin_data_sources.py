from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AdminDataSourceStats(BaseModel):
    received_last_24h: int = 0
    pending_count: int = 0
    error_count: int = 0
    last_received_at: Optional[datetime] = None
    last_processed_at: Optional[datetime] = None


class AdminDataSourceConfig(BaseModel):
    source: str
    display_name: Optional[str] = None
    is_enabled: bool
    rate_limit_per_minute: int
    has_secret: bool
    stats: AdminDataSourceStats


class AdminDataSourceUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=120)
    is_enabled: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=100000)
    # When provided as empty string, the server will clear the stored secret.
    hmac_secret: Optional[str] = Field(None, max_length=4096)


class AdminRotateSecretResponse(BaseModel):
    source: str
    hmac_secret: str

