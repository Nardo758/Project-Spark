"""
Pydantic schemas for two-factor authentication
"""

from pydantic import BaseModel
from typing import List, Optional


class TwoFactorSetupResponse(BaseModel):
    """Response when initiating 2FA setup"""
    secret: str
    qr_code: str  # Base64-encoded QR code image
    backup_codes: Optional[List[str]] = None


class TwoFactorEnableRequest(BaseModel):
    """Request to enable 2FA after setup"""
    otp_code: str


class TwoFactorDisableRequest(BaseModel):
    """Request to disable 2FA"""
    password: str


class TwoFactorVerifyRequest(BaseModel):
    """Request to verify OTP during login"""
    email: str
    otp_code: str


class TwoFactorStatusResponse(BaseModel):
    """Response for 2FA status"""
    enabled: bool
    backup_codes_count: int


class BackupCodesResponse(BaseModel):
    """Response with new backup codes"""
    backup_codes: List[str]
    count: int
