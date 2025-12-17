"""
Replit Auth Router - OAuth integration for Google, GitHub, and other providers
Uses Replit's OpenID Connect provider for seamless social login
"""
import os
import secrets
import httpx
from datetime import timedelta
from urllib.parse import urlencode
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from authlib.common.security import generate_token

from app.db.database import get_db
from app.models.user import User
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter()

# Replit OIDC configuration
REPL_ID = os.environ.get('REPL_ID', '')
ISSUER_URL = os.environ.get('ISSUER_URL', 'https://replit.com/oidc')

# In-memory state storage (for PKCE flow)
# In production, use Redis or database
_auth_states = {}


def get_base_url(request: Request) -> str:
    """Get the base URL for OAuth callbacks"""
    # Check for forwarded headers (behind proxy)
    forwarded_proto = request.headers.get('x-forwarded-proto', 'https')
    forwarded_host = request.headers.get('x-forwarded-host') or request.headers.get('host')
    
    if forwarded_host:
        return f"{forwarded_proto}://{forwarded_host}"
    return str(request.base_url).rstrip('/')


@router.get("/login")
async def replit_login(request: Request, redirect_url: Optional[str] = None):
    """Initiate Replit OAuth login flow"""
    if not REPL_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Replit Auth not configured - REPL_ID not set"
        )
    
    # Generate PKCE code verifier and challenge
    code_verifier = generate_token(64)
    import hashlib
    import base64
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state and code verifier
    _auth_states[state] = {
        'code_verifier': code_verifier,
        'redirect_url': redirect_url or '/discover.html'
    }
    
    # Build authorization URL
    base_url = get_base_url(request)
    callback_url = f"{base_url}/api/v1/replit-auth/callback"
    
    params = {
        'client_id': REPL_ID,
        'response_type': 'code',
        'redirect_uri': callback_url,
        'scope': 'openid profile email',
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'prompt': 'login consent'
    }
    
    auth_url = f"{ISSUER_URL}/auth?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def replit_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from Replit"""
    if error:
        return RedirectResponse(url=f"/signin.html?error={error}")
    
    if not code or not state:
        return RedirectResponse(url="/signin.html?error=missing_params")
    
    # Verify state
    stored_data = _auth_states.pop(state, None)
    if not stored_data:
        return RedirectResponse(url="/signin.html?error=invalid_state")
    
    code_verifier = stored_data['code_verifier']
    redirect_url = stored_data['redirect_url']
    
    # Exchange code for tokens
    base_url = get_base_url(request)
    callback_url = f"{base_url}/api/v1/replit-auth/callback"
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': callback_url,
        'client_id': REPL_ID,
        'code_verifier': code_verifier
    }
    
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                f"{ISSUER_URL}/token",
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if token_response.status_code != 200:
                return RedirectResponse(url=f"/signin.html?error=token_exchange_failed")
            
            tokens = token_response.json()
    except Exception as e:
        print(f"Token exchange error: {e}")
        return RedirectResponse(url="/signin.html?error=token_exchange_error")
    
    # Decode ID token to get user info
    id_token = tokens.get('id_token')
    if not id_token:
        return RedirectResponse(url="/signin.html?error=no_id_token")
    
    # Decode JWT (without verification since it's from Replit)
    import jwt
    try:
        user_claims = jwt.decode(id_token, options={"verify_signature": False})
    except Exception as e:
        print(f"JWT decode error: {e}")
        return RedirectResponse(url="/signin.html?error=invalid_token")
    
    # Extract user info
    replit_user_id = user_claims.get('sub')
    email = user_claims.get('email')
    first_name = user_claims.get('first_name', '')
    last_name = user_claims.get('last_name', '')
    profile_image = user_claims.get('profile_image_url')
    
    if not replit_user_id:
        return RedirectResponse(url="/signin.html?error=no_user_id")
    
    # Find or create user
    # First try to find by OAuth ID
    user = db.query(User).filter(
        User.oauth_provider == 'replit',
        User.oauth_id == replit_user_id
    ).first()
    
    if not user and email:
        # Try to find by email and link accounts
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Link existing account to Replit
            user.oauth_provider = 'replit'
            user.oauth_id = replit_user_id
            if profile_image:
                user.avatar_url = profile_image
    
    if not user:
        # Create new user
        full_name = f"{first_name} {last_name}".strip() or email or f"User_{replit_user_id}"
        user = User(
            email=email,
            name=full_name,
            oauth_provider='replit',
            oauth_id=replit_user_id,
            avatar_url=profile_image,
            is_active=True,
            is_verified=True  # OAuth users are auto-verified
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    # Create JWT token for the app
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Prepare user data for frontend
    user_data = {
        "id": user.id,
        "email": user.email,
        "full_name": user.name,
        "avatar_url": user.avatar_url,
        "is_verified": user.is_verified,
        "is_admin": user.is_admin
    }
    
    # Redirect to frontend with token
    import json
    import base64
    user_json = base64.urlsafe_b64encode(json.dumps(user_data).encode()).decode()
    
    return RedirectResponse(
        url=f"/auth-callback.html?token={access_token}&user={user_json}&redirect={redirect_url}"
    )


@router.get("/logout")
async def replit_logout(request: Request):
    """Logout and end Replit session"""
    base_url = get_base_url(request)
    
    # Redirect to Replit's end session endpoint
    params = {
        'client_id': REPL_ID,
        'post_logout_redirect_uri': base_url
    }
    
    logout_url = f"{ISSUER_URL}/session/end?{urlencode(params)}"
    return RedirectResponse(url=logout_url)


@router.get("/status")
async def auth_status():
    """Check if Replit Auth is configured"""
    return {
        "configured": bool(REPL_ID),
        "provider": "replit"
    }
