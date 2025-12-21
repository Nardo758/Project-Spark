from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.api_key import APIKey
from app.models.opportunity import Opportunity
from app.models.subscription import SubscriptionTier
from app.models.user import User
from app.schemas.developer import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyOut, PublicApiOpportunityList
from app.services.audit import log_event
from app.services.usage_service import usage_service
from app.core.api_key_auth import require_api_key


router = APIRouter()


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _make_key() -> str:
    # "og_" prefix makes it obvious + lets us expose a prefix safely.
    return "og_" + secrets.token_urlsafe(32)


def _prefix(raw: str) -> str:
    return raw[:8]


@router.get("/developer/api-keys", response_model=List[ApiKeyOut])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id)
        .order_by(APIKey.created_at.desc())
        .all()
    )


@router.post("/developer/api-keys", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Require a paid tier for API key access.
    sub = usage_service.get_or_create_subscription(current_user, db)
    tier = sub.tier if isinstance(sub.tier, SubscriptionTier) else SubscriptionTier(sub.tier)
    if tier not in (SubscriptionTier.BUSINESS, SubscriptionTier.ENTERPRISE):
        raise HTTPException(status_code=403, detail="API access requires Business tier or higher")

    raw = _make_key()
    row = APIKey(
        user_id=current_user.id,
        name=payload.name,
        prefix=_prefix(raw),
        key_hash=_hash_key(raw),
        scopes_json=json.dumps(payload.scopes),
        is_active=True,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    log_event(
        db,
        action="developer.api_key.created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="api_key",
        resource_id=row.id,
        metadata={"prefix": row.prefix, "scopes": payload.scopes},
    )

    return ApiKeyCreateResponse(api_key=raw, key=row)


@router.post("/developer/api-keys/{key_id}/revoke", response_model=ApiKeyOut)
def revoke_api_key(
    key_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="API key not found")
    row.is_active = False
    row.revoked_at = datetime.utcnow()
    db.commit()
    db.refresh(row)

    log_event(
        db,
        action="developer.api_key.revoked",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="api_key",
        resource_id=row.id,
        metadata={"prefix": row.prefix},
    )

    return row


@router.get("/public-api/opportunities", response_model=PublicApiOpportunityList)
def public_api_opportunities(
    api_key: APIKey = Depends(require_api_key),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 25,
):
    query = db.query(Opportunity).filter(Opportunity.status == "active").order_by(Opportunity.created_at.desc())
    total = query.count()
    rows = query.offset(skip).limit(limit).all()
    return PublicApiOpportunityList(
        opportunities=rows,  # pydantic will pick fields by name
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )

