"""
Replit Auth Router - OIDC integration using Replit as identity provider
Uses OIDC discovery for endpoint configuration
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

# Replit OIDC configuration from discovery document
REPL_ID = os.environ.get('REPL_ID', '')
ISSUER_URL = "https://replit.com/oidc"
AUTHORIZATION_ENDPOINT = f"{ISSUER_URL}/auth"
TOKEN_ENDPOINT = f"{ISSUER_URL}/token"
END_SESSION_ENDPOINT = f"{ISSUER_URL}/session/end"
JWKS_URL = f"{ISSUER_URL}/jwks"

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


def get_callback_url() -> str:
    """Get the fixed callback URL for OAuth"""
    replit_domain = os.environ.get('REPLIT_DEV_DOMAIN')
    if replit_domain:
        return f"https://{replit_domain}/api/v1/replit-auth/callback"
    return "http://localhost:5000/api/v1/replit-auth/callback"


def verify_id_token(id_token: str, nonce: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify and decode the ID token from Replit.
    Validates signature, issuer, audience, expiry, and nonce.
    """
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256", "PS256"],
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
        
        if nonce and claims.get('nonce') != nonce:
            raise ValueError("Nonce mismatch - possible replay attack")
        
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
    """Initiate Replit OIDC login flow with PKCE"""
    if not REPL_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Replit Auth not configured - REPL_ID not set"
        )
    
    cleanup_expired_states()
    
    code_verifier = generate_token(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    
    callback_url = get_callback_url()
    
    _auth_states[state] = {
        'code_verifier': code_verifier,
        'nonce': nonce,
        'redirect_url': redirect_url or '/discover.html',
        'callback_url': callback_url,
        'created_at': time.time()
    }
    
    params = {
        'client_id': REPL_ID,
        'response_type': 'code',
        'redirect_uri': callback_url,
        'scope': 'openid profile email',
        'state': state,
        'nonce': nonce,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    
    auth_url = f"{AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
    
    print(f"[Replit Auth] === Authorization Request ===")
    print(f"[Replit Auth] Client ID: {REPL_ID}")
    print(f"[Replit Auth] Redirect URI: {callback_url}")
    print(f"[Replit Auth] Auth URL: {auth_url}")
    
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/callback")
async def replit_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle OIDC callback from Replit"""
    print(f"[Replit Auth] === Callback Received ===")
    print(f"[Replit Auth] Code: {'present' if code else 'missing'}")
    print(f"[Replit Auth] State: {'present' if state else 'missing'}")
    print(f"[Replit Auth] Error: {error}")
    print(f"[Replit Auth] Error Description: {error_description}")
    
    if error:
        return RedirectResponse(url=f"/signin.html?error={error}&desc={error_description or ''}")
    
    if not code or not state:
        return RedirectResponse(url="/signin.html?error=missing_params")
    
    cleanup_expired_states()
    stored_data = _auth_states.pop(state, None)
    if not stored_data:
        print(f"[Replit Auth] Invalid state - not found in storage")
        return RedirectResponse(url="/signin.html?error=invalid_state")
    
    if time.time() - stored_data.get('created_at', 0) > STATE_TTL_SECONDS:
        return RedirectResponse(url="/signin.html?error=state_expired")
    
    code_verifier = stored_data['code_verifier']
    nonce = stored_data['nonce']
    redirect_url = stored_data['redirect_url']
    callback_url = stored_data['callback_url']
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': callback_url,
        'client_id': REPL_ID,
        'code_verifier': code_verifier
    }
    
    print(f"[Replit Auth] Exchanging code for tokens...")
    print(f"[Replit Auth] Token endpoint: {TOKEN_ENDPOINT}")
    print(f"[Replit Auth] Redirect URI for token: {callback_url}")
    
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                TOKEN_ENDPOINT,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            print(f"[Replit Auth] Token response status: {token_response.status_code}")
            
            if token_response.status_code != 200:
                print(f"[Replit Auth] Token exchange failed: {token_response.text}")
                return RedirectResponse(url="/signin.html?error=token_exchange_failed")
            
            tokens = token_response.json()
    except Exception as e:
        print(f"[Replit Auth] Token exchange error: {e}")
        return RedirectResponse(url="/signin.html?error=token_exchange_error")
    
    id_token = tokens.get('id_token')
    if not id_token:
        print(f"[Replit Auth] No ID token in response")
        return RedirectResponse(url="/signin.html?error=no_id_token")
    
    try:
        user_claims = verify_id_token(id_token, nonce)
        print(f"[Replit Auth] Token verified successfully")
        print(f"[Replit Auth] User claims: {json.dumps(user_claims, default=str)}")
    except ValueError as e:
        print(f"[Replit Auth] Token verification failed: {e}")
        return RedirectResponse(url="/signin.html?error=token_verification_failed")
    
    replit_user_id = user_claims.get('sub')
    email = user_claims.get('email')
    first_name = user_claims.get('first_name', '')
    last_name = user_claims.get('last_name', '')
    username = user_claims.get('username', '')
    profile_image = user_claims.get('profile_image_url')
    
    if not replit_user_id:
        return RedirectResponse(url="/signin.html?error=no_user_id")
    
    user = db.query(User).filter(
        User.oauth_provider == 'replit',
        User.oauth_id == replit_user_id
    ).first()
    
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.oauth_provider = 'replit'
            user.oauth_id = replit_user_id
            if profile_image:
                user.avatar_url = profile_image
    
    if not user:
        full_name = f"{first_name} {last_name}".strip() or username or f"User_{replit_user_id}"
        user_email = email if email else f"{replit_user_id}@replit.user"
        
        user = User(
            email=user_email,
            name=full_name,
            oauth_provider='replit',
            oauth_id=replit_user_id,
            avatar_url=profile_image,
            is_active=True,
            is_verified=True
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    print(f"[Replit Auth] User authenticated: {user.email}")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    user_data = {
        "id": user.id,
        "email": user.email,
        "full_name": user.name,
        "avatar_url": user.avatar_url,
        "is_verified": user.is_verified,
        "is_admin": user.is_admin
    }
    
    user_json = base64.urlsafe_b64encode(json.dumps(user_data).encode()).decode()
    
    return RedirectResponse(
        url=f"/auth-callback.html?token={access_token}&user={user_json}&redirect={redirect_url}"
    )


@router.get("/logout")
async def replit_logout():
    """Logout and end Replit session"""
    callback_url = get_callback_url()
    base_url = callback_url.rsplit('/api/', 1)[0]
    
    params = {
        'client_id': REPL_ID,
        'post_logout_redirect_uri': base_url
    }
    
    logout_url = f"{END_SESSION_ENDPOINT}?{urlencode(params)}"
    return RedirectResponse(url=logout_url)


@router.get("/status")
async def auth_status():
    """Check if Replit Auth is configured"""
    callback_url = get_callback_url()
    return {
        "configured": bool(REPL_ID),
        "provider": "replit",
        "client_id": REPL_ID,
        "callback_url": callback_url,
        "authorization_endpoint": AUTHORIZATION_ENDPOINT,
        "token_endpoint": TOKEN_ENDPOINT
    }


@router.get("/debug")
async def auth_debug():
    """Debug endpoint to show current configuration"""
    return {
        "repl_id": REPL_ID,
        "replit_dev_domain": os.environ.get('REPLIT_DEV_DOMAIN', 'not set'),
        "callback_url": get_callback_url(),
        "issuer": ISSUER_URL,
        "authorization_endpoint": AUTHORIZATION_ENDPOINT,
        "token_endpoint": TOKEN_ENDPOINT,
        "jwks_url": JWKS_URL
    }
