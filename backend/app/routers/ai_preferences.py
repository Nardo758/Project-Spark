"""
AI Preferences API Router
Manages user AI provider preferences for the Dual-Realm Workspace
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging
import os

from app.db.database import get_db
from app.models.user import User, UserAIPreference
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-preferences", tags=["AI Preferences"])


class AIPreferencesResponse(BaseModel):
    provider: str
    mode: str
    model: Optional[str] = None
    has_openai_key: bool = False
    has_claude_key: bool = False
    openai_key_validated_at: Optional[datetime] = None
    claude_key_validated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIPreferencesUpdate(BaseModel):
    provider: Optional[str] = Field(None, description="AI provider: 'claude' or 'openai'")
    mode: Optional[str] = Field(None, description="Mode: 'replit' or 'byok'")
    model: Optional[str] = Field(None, description="Specific model to use")


class OpenAIKeyUpdate(BaseModel):
    api_key: str = Field(..., min_length=20, description="OpenAI API key")


class KeyValidationResponse(BaseModel):
    valid: bool
    message: str
    provider: str


@router.get("", response_model=AIPreferencesResponse)
async def get_ai_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's AI provider preferences"""
    prefs = db.query(UserAIPreference).filter(
        UserAIPreference.user_id == current_user.id
    ).first()
    
    if not prefs:
        return AIPreferencesResponse(
            provider="claude",
            mode="replit",
            model=None,
            has_openai_key=False,
            has_claude_key=bool(current_user.encrypted_claude_api_key),
            openai_key_validated_at=None,
            claude_key_validated_at=current_user.claude_key_validated_at
        )
    
    return AIPreferencesResponse(
        provider=prefs.provider or "claude",
        mode=prefs.mode or "replit",
        model=prefs.model,
        has_openai_key=bool(prefs.encrypted_openai_api_key),
        has_claude_key=bool(current_user.encrypted_claude_api_key),
        openai_key_validated_at=prefs.openai_key_validated_at,
        claude_key_validated_at=current_user.claude_key_validated_at
    )


@router.put("", response_model=AIPreferencesResponse)
async def update_ai_preferences(
    update: AIPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's AI provider preferences"""
    prefs = db.query(UserAIPreference).filter(
        UserAIPreference.user_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = UserAIPreference(user_id=current_user.id)
        db.add(prefs)
    
    if update.provider is not None:
        if update.provider not in ["claude", "openai"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid provider. Must be 'claude' or 'openai'"
            )
        prefs.provider = update.provider
    
    if update.mode is not None:
        if update.mode not in ["replit", "byok"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid mode. Must be 'replit' or 'byok'"
            )
        prefs.mode = update.mode
    
    if update.model is not None:
        prefs.model = update.model
    
    db.commit()
    db.refresh(prefs)
    
    from app.services.ai_provider_service import ai_provider_service
    ai_provider_service.clear_cache(current_user.id)
    
    return AIPreferencesResponse(
        provider=prefs.provider or "claude",
        mode=prefs.mode or "replit",
        model=prefs.model,
        has_openai_key=bool(prefs.encrypted_openai_api_key),
        has_claude_key=bool(current_user.encrypted_claude_api_key),
        openai_key_validated_at=prefs.openai_key_validated_at,
        claude_key_validated_at=current_user.claude_key_validated_at
    )


@router.post("/openai-key", response_model=KeyValidationResponse)
async def set_openai_api_key(
    key_update: OpenAIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set and validate OpenAI API key for BYOK"""
    from openai import OpenAI
    
    api_key = key_update.api_key.strip()
    if not api_key.startswith("sk-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OpenAI API key format. Key should start with 'sk-'"
        )
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.models.list()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not validate API key - no models accessible"
            )
    except Exception as e:
        logger.error(f"OpenAI key validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OpenAI API key: {str(e)}"
        )
    
    prefs = db.query(UserAIPreference).filter(
        UserAIPreference.user_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = UserAIPreference(user_id=current_user.id)
        db.add(prefs)
    
    prefs.set_openai_api_key(api_key)
    prefs.openai_key_validated_at = datetime.utcnow()
    prefs.provider = "openai"
    prefs.mode = "byok"
    
    db.commit()
    
    from app.services.ai_provider_service import ai_provider_service
    ai_provider_service.clear_cache(current_user.id)
    
    return KeyValidationResponse(
        valid=True,
        message="OpenAI API key validated and saved successfully",
        provider="openai"
    )


@router.delete("/openai-key")
async def remove_openai_api_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove stored OpenAI API key"""
    prefs = db.query(UserAIPreference).filter(
        UserAIPreference.user_id == current_user.id
    ).first()
    
    if prefs:
        prefs.encrypted_openai_api_key = None
        prefs.openai_key_validated_at = None
        if prefs.provider == "openai" and prefs.mode == "byok":
            prefs.mode = "replit"
        db.commit()
    
    from app.services.ai_provider_service import ai_provider_service
    ai_provider_service.clear_cache(current_user.id)
    
    return {"message": "OpenAI API key removed successfully"}


@router.get("/available-providers")
async def get_available_providers():
    """Get list of available AI providers and their capabilities"""
    return {
        "providers": [
            {
                "id": "claude",
                "name": "Claude",
                "description": "Anthropic's Claude AI",
                "modes": [
                    {"id": "replit", "name": "Replit AI", "description": "Uses Replit credits, no API key needed"},
                    {"id": "byok", "name": "Your API Key", "description": "Use your own Anthropic API key"}
                ],
                "models": [
                    {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "default": True},
                    {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
                ]
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "description": "OpenAI's GPT models",
                "modes": [
                    {"id": "replit", "name": "Replit AI", "description": "Uses Replit credits, no API key needed"},
                    {"id": "byok", "name": "Your API Key", "description": "Use your own OpenAI API key for billing tracking"}
                ],
                "models": [
                    {"id": "gpt-5", "name": "GPT-5", "default": True, "replit_only": True},
                    {"id": "gpt-4o", "name": "GPT-4o"},
                    {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
                ]
            }
        ]
    }
