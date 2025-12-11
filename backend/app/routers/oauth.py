"""
OAuth Authentication Router

Endpoints for OAuth login with Google and GitHub
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.database import get_db
from app.models.user import User
from app.services.oauth import oauth_service
from app.core.security import create_access_token
from app.core.config import settings
from app.core.dependencies import get_current_user

router = APIRouter()

# In-memory state storage (in production, use Redis or database)
# Format: {state_token: {provider, redirect_uri, created_at}}
oauth_states = {}


@router.get("/{provider}/login")
async def oauth_login(
    provider: str,
    redirect_uri: str = Query(..., description="Frontend callback URL")
):
    """
    Initiate OAuth login flow

    Args:
        provider: OAuth provider ('google' or 'github')
        redirect_uri: Frontend URL to redirect after authentication
    """
    if provider not in ["google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider"
        )

    # Generate state for CSRF protection
    state = oauth_service.generate_state()

    # Store state temporarily (expires in 10 minutes)
    oauth_states[state] = {
        "provider": provider,
        "frontend_redirect": redirect_uri,
    }

    # Build backend callback URL
    backend_callback = f"{settings.BACKEND_URL}/api/v1/oauth/{provider}/callback"

    # Get authorization URL
    auth_url = oauth_service.get_authorization_url(
        provider=provider,
        redirect_uri=backend_callback,
        state=state
    )

    return {"authorization_url": auth_url}


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from provider

    Args:
        provider: OAuth provider
        code: Authorization code from provider
        state: State token for CSRF verification
    """
    # Verify state
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token"
        )

    state_data = oauth_states.pop(state)
    frontend_redirect = state_data.get("frontend_redirect")

    # Build backend callback URL
    backend_callback = f"{settings.BACKEND_URL}/api/v1/oauth/{provider}/callback"

    # Complete OAuth flow
    user_info = await oauth_service.complete_oauth_flow(
        provider=provider,
        code=code,
        redirect_uri=backend_callback
    )

    if not user_info or not user_info.get("email"):
        # Redirect to frontend with error
        error_url = f"{frontend_redirect}?error=oauth_failed"
        return RedirectResponse(url=error_url)

    # Check if user exists
    user = db.query(User).filter(User.email == user_info["email"]).first()

    if user:
        # Update OAuth info if not set
        if not user.oauth_provider:
            user.oauth_provider = user_info["provider"]
            user.oauth_id = user_info["provider_user_id"]
            user.avatar_url = user.avatar_url or user_info.get("avatar_url")
            db.commit()
    else:
        # Create new user
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            avatar_url=user_info.get("avatar_url"),
            oauth_provider=user_info["provider"],
            oauth_id=user_info["provider_user_id"],
            is_verified=user_info.get("email_verified", True),
            hashed_password=None  # OAuth users don't have passwords
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    # Redirect to frontend with token
    success_url = f"{frontend_redirect}?token={access_token}&provider={provider}"
    return RedirectResponse(url=success_url)


@router.post("/{provider}/connect")
async def connect_oauth_account(
    provider: str,
    code: str,
    redirect_uri: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect OAuth account to existing user account

    This allows users to link their Google/GitHub account to their existing account
    """
    if provider not in ["google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider"
        )

    # Complete OAuth flow
    user_info = await oauth_service.complete_oauth_flow(
        provider=provider,
        code=code,
        redirect_uri=redirect_uri
    )

    if not user_info or not user_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from OAuth provider"
        )

    # Check if email matches current user
    if user_info["email"] != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth account email does not match your account email"
        )

    # Check if another user already linked this OAuth account
    existing = db.query(User).filter(
        User.oauth_provider == provider,
        User.oauth_id == user_info["provider_user_id"],
        User.id != current_user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This OAuth account is already linked to another user"
        )

    # Link OAuth account
    current_user.oauth_provider = provider
    current_user.oauth_id = user_info["provider_user_id"]
    db.commit()

    return {
        "message": f"{provider.capitalize()} account connected successfully",
        "provider": provider
    }


@router.delete("/{provider}/disconnect")
async def disconnect_oauth_account(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect OAuth account from user

    Note: Users must have a password set before disconnecting OAuth
    """
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must set a password before disconnecting OAuth login"
        )

    if current_user.oauth_provider != provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No {provider} account connected"
        )

    # Disconnect OAuth
    current_user.oauth_provider = None
    current_user.oauth_id = None
    db.commit()

    return {
        "message": f"{provider.capitalize()} account disconnected successfully"
    }


# Import get_current_user at the end to avoid circular import
from app.core.dependencies import get_current_user
