from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.token import Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.core.tokens import (
    generate_verification_token,
    get_verification_token_expiry,
    generate_password_reset_token,
    get_password_reset_token_expiry,
    is_token_expired
)
from app.services.email import email_service

router = APIRouter()


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: str


class RequestPasswordResetRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and send verification email"""
    # Check if user exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Generate verification token
    verification_token = generate_verification_token()
    token_expiry = get_verification_token_expiry()

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        bio=user_data.bio,
        hashed_password=hashed_password,
        verification_token=verification_token,
        verification_token_expires=token_expiry,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    try:
        email_service.send_verification_email(
            to_email=new_user.email,
            verification_token=verification_token,
            user_name=new_user.name
        )
    except Exception as e:
        # Log error but don't fail registration
        print(f"Failed to send verification email: {e}")

    return new_user


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Check if 2FA is enabled
    if user.otp_enabled:
        return {
            "requires_2fa": True,
            "email": user.email,
            "message": "Please provide your 2FA code"
        }

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_2fa": False
    }


@router.post("/verify-email")
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify user's email address using token"""
    user = db.query(User).filter(User.verification_token == request.token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    if user.is_verified:
        return {
            "message": "Email already verified",
            "already_verified": True
        }

    # Check if token is expired
    if is_token_expired(user.verification_token_expires):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new one."
        )

    # Verify the user
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None

    db.commit()

    return {
        "message": "Email verified successfully",
        "email": user.email
    }


@router.post("/resend-verification")
def resend_verification(request: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend verification email to user"""
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        # Don't reveal if email exists or not for security
        return {
            "message": "If the email exists and is not verified, a verification email will be sent"
        }

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # Generate new verification token
    verification_token = generate_verification_token()
    token_expiry = get_verification_token_expiry()

    user.verification_token = verification_token
    user.verification_token_expires = token_expiry

    db.commit()

    # Send verification email
    try:
        email_service.send_verification_email(
            to_email=user.email,
            verification_token=verification_token,
            user_name=user.name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

    return {
        "message": "Verification email sent successfully"
    }


@router.post("/request-password-reset")
def request_password_reset(request: RequestPasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset email"""
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        # Don't reveal if email exists or not for security
        return {
            "message": "If the email exists, a password reset link will be sent"
        }

    # Generate password reset token
    reset_token = generate_password_reset_token()
    token_expiry = get_password_reset_token_expiry()

    user.password_reset_token = reset_token
    user.password_reset_token_expires = token_expiry

    db.commit()

    # Send password reset email
    try:
        email_service.send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            user_name=user.name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email"
        )

    return {
        "message": "Password reset email sent successfully"
    }


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token"""
    user = db.query(User).filter(User.password_reset_token == request.token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset token"
        )

    # Check if token is expired
    if is_token_expired(user.password_reset_token_expires):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired. Please request a new one."
        )

    # Validate new password length
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None

    db.commit()

    return {
        "message": "Password reset successfully",
        "email": user.email
    }
