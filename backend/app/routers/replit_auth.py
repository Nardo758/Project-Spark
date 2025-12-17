"""
Replit Auth Router - OAuth integration for Google, GitHub, and other providers
Uses Replit's OpenID Connect provider for seamless social login
"""
import os
import secrets
import httpx
import time
import hashlib
import base64
import json
from datetime import timedelta
from urllib.parse import urlencode
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.common.security import generate_token
import jwt
from jwt import PyJWKClient

from app.db.database import get_db
from app.models.user import User
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter()

# Replit OIDC configuration
REPL_ID = os.environ.get('REPL_ID', '')
ISSUER_URL = os.environ.get('ISSUER_URL', 'https://replit.com/oidc')
JWKS_URL = f"{ISSUER_URL}/.well-known/jwks.json"

# State storage with TTL (5 minutes)
STATE_TTL_SECONDS = 300
_auth_states: Dict[str, Dict[str, Any]] = {}

# JWKS client for signature verification (cached)
_jwks_client = None


def get_jwks_client():
    """Get cached JWKS client for token verification"""
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(JWKS_URL, cache_keys=True)
    return _jwks_client


def cleanup_expired_states():
    """Remove expired states from memory"""
    current_time = time.time()
    expired_keys = [
        key for key, value in _auth_states.items()
        if current_time - value.get('created_at', 0) > STATE_TTL_SECONDS
    ]
    for key in expired_keys:
        _auth_states.pop(key, None)


def get_base_url(request: Request) -> str:
    """Get the base URL for OAuth callbacks"""
    # Use REPLIT_DEV_DOMAIN for consistent OAuth redirect URIs
    replit_domain = os.environ.get('REPLIT_DEV_DOMAIN')
    if replit_domain:
        return f"https://{replit_domain}"
    
    # Fallback to request headers
    forwarded_proto = request.headers.get('x-forwarded-proto', 'https')
    forwarded_host = request.headers.get('x-forwarded-host') or request.headers.get('host')
    
    if forwarded_host:
        return f"{forwarded_proto}://{forwarded_host}"
    return str(request.base_url).rstrip('/')


def verify_id_token(id_token: str) -> Dict[str, Any]:
    """
    Verify and decode the ID token from Replit.
    Validates signature, issuer, audience, and expiry.
    """
    try:
        # Get the signing key from JWKS
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        
        # Decode and verify the token
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=ISSUER_URL,
            audience=REPL_ID,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
                "verify_aud": True,
            }
        )
        return claims
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidIssuerError:
        raise ValueError("Invalid token issuer")
    except jwt.InvalidAudienceError:
        raise ValueError("Invalid token audience")
    except jwt.InvalidSignatureError:
        raise ValueError("Invalid token signature")
    except Exception as e:
        raise ValueError(f"Token validation failed: {str(e)}")


@router.get("/login")
async def replit_login(request: Request, redirect_url: Optional[str] = None):
    """Initiate Replit OAuth login flow"""
    if not REPL_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Replit Auth not configured - REPL_ID not set"
        )
    
    # Cleanup expired states
    cleanup_expired_states()
    
    # Generate PKCE code verifier and challenge
    code_verifier = generate_token(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state with TTL
    _auth_states[state] = {
        'code_verifier': code_verifier,
        'redirect_url': redirect_url or '/discover.html',
        'created_at': time.time()
    }
    
    # Build authorization URL
    base_url = get_base_url(request)
    callback_url = f"{base_url}/api/v1/replit-auth/callback"
    
    params = {
        'client_id': REPL_ID,
        'response_type': 'code',
        'redirect_uri': callback_url,
        'scope': 'openid profile email offline_access',
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'prompt': 'login consent'
    }
    
    print(f"[Replit Auth] Redirecting to: {ISSUER_URL}/auth")
    print(f"[Replit Auth] Callback URL: {callback_url}")
    print(f"[Replit Auth] Client ID: {REPL_ID}")
    
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
    
    # Cleanup and verify state
    cleanup_expired_states()
    stored_data = _auth_states.pop(state, None)
    if not stored_data:
        return RedirectResponse(url="/signin.html?error=invalid_state")
    
    # Check if state is expired
    if time.time() - stored_data.get('created_at', 0) > STATE_TTL_SECONDS:
        return RedirectResponse(url="/signin.html?error=state_expired")
    
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
                print(f"Token exchange failed: {token_response.text}")
                return RedirectResponse(url="/signin.html?error=token_exchange_failed")
            
            tokens = token_response.json()
    except Exception as e:
        print(f"Token exchange error: {e}")
        return RedirectResponse(url="/signin.html?error=token_exchange_error")
    
    # Get and verify ID token
    id_token = tokens.get('id_token')
    if not id_token:
        return RedirectResponse(url="/signin.html?error=no_id_token")
    
    # Verify ID token signature, issuer, audience, and expiry
    try:
        user_claims = verify_id_token(id_token)
    except ValueError as e:
        print(f"Token verification failed: {e}")
        return RedirectResponse(url="/signin.html?error=token_verification_failed")
    
    # Extract user info
    replit_user_id = user_claims.get('sub')
    email = user_claims.get('email')  # May be None
    first_name = user_claims.get('first_name', '')
    last_name = user_claims.get('last_name', '')
    profile_image = user_claims.get('profile_image_url')
    
    if not replit_user_id:
        return RedirectResponse(url="/signin.html?error=no_user_id")
    
    # Find or create user
    # First try to find by OAuth ID (stable identifier)
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
        full_name = f"{first_name} {last_name}".strip() or f"User_{replit_user_id}"
        
        # Generate a placeholder email if not provided
        user_email = email if email else f"{replit_user_id}@replit.user"
        
        user = User(
            email=user_email,
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
    
    # Create JWT token for the app using user ID (stable identifier)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
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
