import os
import secrets
import logging
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
import httpx
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.expert import Expert
from app.core.security import create_access_token, get_password_hash
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"

STATE_EXPIRY_MINUTES = 10
CODE_EXPIRY_MINUTES = 5
oauth_states: dict[str, dict] = {}
auth_codes: dict[str, dict] = {}


def get_redirect_uri():
    domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:8000")
    protocol = "https" if "replit" in domain else "http"
    return f"{protocol}://{domain}/api/v1/auth/linkedin/callback"


def cleanup_expired_states():
    """Remove expired OAuth states and auth codes"""
    now = datetime.now(timezone.utc)
    expired = [k for k, v in oauth_states.items() if v.get("expires_at", now) < now]
    for k in expired:
        del oauth_states[k]
    
    expired_codes = [k for k, v in auth_codes.items() if v.get("expires_at", now) < now]
    for k in expired_codes:
        del auth_codes[k]


@router.get("/login")
async def linkedin_login(
    role: str = Query(..., description="Role to join: expert, investor, partner, lender")
):
    if not LINKEDIN_CLIENT_ID:
        raise HTTPException(status_code=500, detail="LinkedIn OAuth not configured")
    
    cleanup_expired_states()
    
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "role": role,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=STATE_EXPIRY_MINUTES)
    }
    
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": get_redirect_uri(),
        "state": state,
        "scope": "openid profile email"
    }
    
    authorization_url = f"{LINKEDIN_AUTHORIZATION_URL}?{urlencode(params)}"
    return RedirectResponse(url=authorization_url)


@router.get("/callback")
async def linkedin_callback(
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    error_description: str = Query(None),
    db: Session = Depends(get_db)
):
    frontend_domain = os.environ.get("REPLIT_DEV_DOMAIN", "localhost:5000")
    frontend_protocol = "https" if "replit" in frontend_domain else "http"
    frontend_base = f"{frontend_protocol}://{frontend_domain}"
    
    if error:
        return RedirectResponse(
            url=f"{frontend_base}/join-network/expert?error={error_description or error}"
        )
    
    if not code or not state:
        return RedirectResponse(
            url=f"{frontend_base}/join-network/expert?error=Missing authorization code"
        )
    
    state_data = oauth_states.pop(state, None)
    if not state_data:
        return RedirectResponse(
            url=f"{frontend_base}/join-network/expert?error=Invalid or expired session. Please try again."
        )
    
    if datetime.now(timezone.utc) > state_data.get("expires_at", datetime.now(timezone.utc)):
        return RedirectResponse(
            url=f"{frontend_base}/join-network/expert?error=Session expired. Please try again."
        )
    
    role = state_data.get("role", "expert")
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            LINKEDIN_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": get_redirect_uri(),
                "client_id": LINKEDIN_CLIENT_ID,
                "client_secret": LINKEDIN_CLIENT_SECRET
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if token_response.status_code != 200:
            logger.error(f"LinkedIn token exchange failed: {token_response.text}")
            return RedirectResponse(
                url=f"{frontend_base}/join-network/{role}?error=Failed to get access token"
            )
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        userinfo_response = await client.get(
            LINKEDIN_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if userinfo_response.status_code != 200:
            logger.error(f"LinkedIn userinfo failed: {userinfo_response.text}")
            return RedirectResponse(
                url=f"{frontend_base}/join-network/{role}?error=Failed to get user info"
            )
        
        user_info = userinfo_response.json()
    
    email = user_info.get("email")
    name = user_info.get("name") or f"{user_info.get('given_name', '')} {user_info.get('family_name', '')}".strip()
    picture = user_info.get("picture")
    linkedin_id = user_info.get("sub")
    
    if not email:
        return RedirectResponse(
            url=f"{frontend_base}/join-network/{role}?error=No email provided by LinkedIn"
        )
    
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            random_password = secrets.token_urlsafe(32)
            user = User(
                email=email,
                name=name,
                hashed_password=get_password_hash(random_password),
                is_verified=True,
                oauth_provider="linkedin",
                oauth_id=linkedin_id,
                avatar_url=picture
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if linkedin_id and not user.oauth_id:
                user.oauth_provider = "linkedin"
                user.oauth_id = linkedin_id
            if picture and not user.avatar_url:
                user.avatar_url = picture
            db.commit()
        
        if role == "expert":
            existing_expert = db.query(Expert).filter(Expert.user_id == user.id).first()
            if not existing_expert:
                expert = Expert(
                    user_id=user.id,
                    name=name,
                    headline="Professional from LinkedIn",
                    bio=None,
                    skills=[],
                    specialization=[],
                    pricing_model="hourly",
                    hourly_rate_cents=0,
                    is_active=True
                )
                db.add(expert)
                db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during LinkedIn OAuth: {e}")
        return RedirectResponse(
            url=f"{frontend_base}/join-network/{role}?error=Account creation failed. Please try again."
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    cleanup_expired_states()
    exchange_code = secrets.token_urlsafe(32)
    auth_codes[exchange_code] = {
        "jwt": jwt_token,
        "user_email": email,
        "name": name,
        "role": role,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=CODE_EXPIRY_MINUTES),
        "used": False
    }
    
    from urllib.parse import quote
    encoded_name = quote(name or "")
    
    return RedirectResponse(
        url=f"{frontend_base}/join-network/{role}?code={exchange_code}&name={encoded_name}",
        status_code=302
    )


@router.post("/redeem")
async def redeem_auth_code(code: str = Query(..., description="Exchange code from LinkedIn callback")):
    """Exchange a one-time code for a JWT token"""
    cleanup_expired_states()
    
    code_data = auth_codes.get(code)
    if not code_data:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    if code_data.get("used"):
        del auth_codes[code]
        raise HTTPException(status_code=400, detail="Code already used")
    
    if datetime.now(timezone.utc) > code_data.get("expires_at", datetime.now(timezone.utc)):
        del auth_codes[code]
        raise HTTPException(status_code=400, detail="Code expired")
    
    del auth_codes[code]
    
    return {
        "access_token": code_data["jwt"],
        "token_type": "bearer",
        "user": {
            "email": code_data["user_email"],
            "name": code_data["name"]
        }
    }
