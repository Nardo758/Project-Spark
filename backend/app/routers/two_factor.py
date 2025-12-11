"""
Two-Factor Authentication Router

Endpoints for managing two-factor authentication (2FA) using TOTP.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.two_factor import (
    TwoFactorSetupResponse,
    TwoFactorEnableRequest,
    TwoFactorDisableRequest,
    TwoFactorVerifyRequest,
    TwoFactorStatusResponse,
    BackupCodesResponse
)
from app.services.two_factor import two_factor_service
from app.core.security import verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.core.config import settings
from datetime import timedelta

router = APIRouter()


@router.post("/setup", response_model=TwoFactorSetupResponse)
def setup_two_factor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate 2FA setup by generating a secret and QR code.
    Does not enable 2FA yet - user must verify OTP first.
    """
    # Generate new secret
    secret = two_factor_service.generate_secret()

    # Generate QR code
    qr_code = two_factor_service.generate_qr_code(
        email=current_user.email,
        secret=secret
    )

    # Temporarily store the secret (not enabled yet)
    current_user.otp_secret = secret
    db.commit()

    return {
        "secret": secret,
        "qr_code": qr_code
    }


@router.post("/enable")
def enable_two_factor(
    request: TwoFactorEnableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enable 2FA after verifying the initial OTP code.
    Also generates backup codes.
    """
    if not current_user.otp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated. Call /setup first."
        )

    if current_user.otp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )

    # Verify the OTP code
    if not two_factor_service.verify_otp(current_user.otp_secret, request.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code"
        )

    # Generate backup codes
    backup_codes, encrypted_codes = two_factor_service.generate_backup_codes()

    # Enable 2FA
    current_user.otp_enabled = True
    current_user.backup_codes = encrypted_codes
    db.commit()

    return {
        "message": "2FA enabled successfully",
        "backup_codes": backup_codes
    }


@router.post("/disable")
def disable_two_factor(
    request: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable 2FA. Requires password verification.
    """
    if not current_user.otp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )

    # Verify password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Disable 2FA and clear related data
    current_user.otp_enabled = False
    current_user.otp_secret = None
    current_user.backup_codes = None
    db.commit()

    return {"message": "2FA disabled successfully"}


@router.post("/verify")
def verify_two_factor_login(
    request: TwoFactorVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP code during login process.
    This is called after initial username/password authentication.
    """
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.otp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account"
        )

    # Try to verify OTP code
    is_valid = two_factor_service.verify_otp(user.otp_secret, request.otp_code)
    used_backup = False

    if not is_valid:
        # Try backup code as fallback
        is_backup_valid, updated_codes = two_factor_service.verify_backup_code(
            user.backup_codes,
            request.otp_code
        )

        if is_backup_valid:
            # Update backup codes (remove used one)
            user.backup_codes = updated_codes
            db.commit()
            used_backup = True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP or backup code"
            )

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "used_backup_code": used_backup
    }


@router.get("/status", response_model=TwoFactorStatusResponse)
def get_two_factor_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current 2FA status for the user.
    """
    backup_count = two_factor_service.get_remaining_backup_codes_count(
        current_user.backup_codes
    )

    return {
        "enabled": current_user.otp_enabled,
        "backup_codes_count": backup_count
    }


@router.post("/regenerate-backup-codes", response_model=BackupCodesResponse)
def regenerate_backup_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate backup codes. Old codes will be invalidated.
    """
    if not current_user.otp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )

    # Generate new backup codes
    backup_codes, encrypted_codes = two_factor_service.generate_backup_codes()

    # Update user
    current_user.backup_codes = encrypted_codes
    db.commit()

    return {
        "backup_codes": backup_codes,
        "count": len(backup_codes)
    }
