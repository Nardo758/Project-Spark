"""BYOK (Bring Your Own Key) API endpoints for managing user API keys."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.encryption_service import encryption_service

router = APIRouter(prefix="/api/byok", tags=["BYOK"])


class SetApiKeyRequest(BaseModel):
    provider: str
    api_key: str


class ApiKeyStatusResponse(BaseModel):
    provider: str
    has_key: bool
    validated_at: str | None = None
    is_valid: bool = False


class ValidateKeyResponse(BaseModel):
    valid: bool
    error: str | None = None


@router.get("/status")
async def get_api_key_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    statuses = {}
    
    if current_user.encrypted_claude_api_key:
        statuses["claude"] = ApiKeyStatusResponse(
            provider="claude",
            has_key=True,
            validated_at=current_user.claude_key_validated_at.isoformat() if current_user.claude_key_validated_at else None,
            is_valid=current_user.claude_key_validated_at is not None
        )
    else:
        statuses["claude"] = ApiKeyStatusResponse(
            provider="claude",
            has_key=False
        )
    
    return {"keys": statuses}


@router.post("/validate")
async def validate_api_key(request: SetApiKeyRequest) -> ValidateKeyResponse:
    if request.provider == "claude":
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": request.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "hi"}]
                    }
                )
                
                if response.status_code == 200:
                    return ValidateKeyResponse(valid=True)
                elif response.status_code == 401:
                    return ValidateKeyResponse(valid=False, error="Invalid API key")
                elif response.status_code == 429:
                    return ValidateKeyResponse(valid=True)
                else:
                    error_data = response.json()
                    return ValidateKeyResponse(
                        valid=False, 
                        error=error_data.get("error", {}).get("message", "Unknown error")
                    )
        except httpx.TimeoutException:
            return ValidateKeyResponse(valid=False, error="Request timed out")
        except Exception as e:
            return ValidateKeyResponse(valid=False, error=str(e))
    
    return ValidateKeyResponse(valid=False, error="Unsupported provider")


@router.post("/set")
async def set_api_key(
    request: SetApiKeyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    validation = await validate_api_key(request)
    if not validation.valid:
        raise HTTPException(status_code=400, detail=validation.error or "Invalid API key")
    
    if request.provider == "claude":
        current_user.encrypted_claude_api_key = encryption_service.encrypt(request.api_key)
        current_user.claude_key_validated_at = datetime.utcnow()
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    db.commit()
    
    return {"success": True, "provider": request.provider, "message": "API key saved and validated"}


@router.delete("/{provider}")
async def remove_api_key(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    if provider == "claude":
        current_user.encrypted_claude_api_key = None
        current_user.claude_key_validated_at = None
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    db.commit()
    
    return {"success": True, "provider": provider, "message": "API key removed"}
