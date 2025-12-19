"""
Magic Link Authentication Router
Passwordless login via email using Resend
"""
import os
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.security import create_access_token
from app.core.config import settings
from app.services.email import email_service

router = APIRouter()

MAGIC_LINK_EXPIRY_MINUTES = 15
_magic_tokens: Dict[str, Dict[str, Any]] = {}


def cleanup_expired_tokens():
    """Remove expired magic link tokens"""
    current_time = time.time()
    expired = [
        token for token, data in _magic_tokens.items()
        if current_time - data.get('created_at', 0) > MAGIC_LINK_EXPIRY_MINUTES * 60
    ]
    for token in expired:
        _magic_tokens.pop(token, None)


def get_frontend_url() -> str:
    """Get the frontend URL for magic links"""
    repl_slug = os.environ.get('REPL_SLUG', '')
    repl_owner = os.environ.get('REPL_OWNER', '')
    replit_dev_domain = os.environ.get('REPLIT_DEV_DOMAIN', '')
    
    if replit_dev_domain:
        return f"https://{replit_dev_domain}"
    elif repl_slug and repl_owner:
        return f"https://{repl_slug}.{repl_owner}.repl.co"
    return os.environ.get('FRONTEND_URL', 'http://localhost:5000')


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkVerify(BaseModel):
    token: str


class MagicLinkResponse(BaseModel):
    message: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


@router.post("/send", response_model=MagicLinkResponse)
async def send_magic_link(request: MagicLinkRequest, db: Session = Depends(get_db)):
    """
    Send a magic link to the user's email.
    Works for both existing users and new signups.
    """
    cleanup_expired_tokens()
    
    email = request.email.lower().strip()
    
    token = secrets.token_urlsafe(32)
    
    _magic_tokens[token] = {
        'email': email,
        'created_at': time.time()
    }
    
    frontend_url = get_frontend_url()
    magic_link = f"{frontend_url}/auth/magic?token={token}"
    
    user = db.query(User).filter(User.email == email).first()
    user_name = user.name if user else "there"
    action_text = "sign in to" if user else "create your account on"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #1c1917;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background: #fafaf9;
            }}
            .container {{
                background: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }}
            .header {{
                background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                color: white;
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .button {{
                display: inline-block;
                padding: 16px 40px;
                background: #7c3aed;
                color: white !important;
                text-decoration: none;
                border-radius: 8px;
                margin: 24px 0;
                font-weight: 600;
                font-size: 16px;
            }}
            .button:hover {{
                background: #6d28d9;
            }}
            .expiry {{
                background: #f5f3ff;
                border-left: 4px solid #7c3aed;
                padding: 12px 16px;
                margin: 20px 0;
                border-radius: 0 8px 8px 0;
                font-size: 14px;
                color: #57534e;
            }}
            .footer {{
                background: #f5f5f4;
                padding: 20px 30px;
                text-align: center;
                font-size: 12px;
                color: #78716c;
            }}
            .link-fallback {{
                font-size: 12px;
                color: #78716c;
                word-break: break-all;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>OppGrid</h1>
            </div>
            <div class="content">
                <h2>Hey {user_name}!</h2>
                <p>Click the button below to {action_text} OppGrid. No password needed!</p>
                
                <div style="text-align: center;">
                    <a href="{magic_link}" class="button">Sign In to OppGrid</a>
                </div>
                
                <div class="expiry">
                    This link expires in {MAGIC_LINK_EXPIRY_MINUTES} minutes and can only be used once.
                </div>
                
                <p class="link-fallback">
                    If the button doesn't work, copy and paste this link into your browser:<br>
                    {magic_link}
                </p>
            </div>
            <div class="footer">
                <p>If you didn't request this email, you can safely ignore it.</p>
                <p>&copy; 2025 OppGrid - The Opportunity Intelligence Platform</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Hey {user_name}!

    Click this link to {action_text} OppGrid:
    {magic_link}

    This link expires in {MAGIC_LINK_EXPIRY_MINUTES} minutes and can only be used once.

    If you didn't request this email, you can safely ignore it.

    - The OppGrid Team
    """
    
    try:
        email_service.send_email(
            to_email=email,
            subject="Your OppGrid Login Link",
            html_content=html_content,
            text_content=text_content
        )
    except Exception as e:
        _magic_tokens.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send magic link email: {str(e)}"
        )
    
    return MagicLinkResponse(
        message="Magic link sent! Check your email.",
        email=email
    )


@router.post("/verify", response_model=TokenResponse)
async def verify_magic_link(request: MagicLinkVerify, db: Session = Depends(get_db)):
    """
    Verify the magic link token and log the user in.
    Creates a new account if the user doesn't exist.
    """
    cleanup_expired_tokens()
    
    token = request.token
    
    token_data = _magic_tokens.pop(token, None)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired magic link. Please request a new one."
        )
    
    if time.time() - token_data['created_at'] > MAGIC_LINK_EXPIRY_MINUTES * 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Magic link has expired. Please request a new one."
        )
    
    email = token_data['email']
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(
            email=email,
            name=email.split('@')[0].title(),
            is_active=True,
            is_verified=True,
            oauth_provider='magic_link'
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if not user.is_verified:
            user.is_verified = True
            db.commit()
    
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
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_data
    )
