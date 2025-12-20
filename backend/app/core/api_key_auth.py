from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.api_key import APIKey


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_api_key_from_headers(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Optional[str]:
    if x_api_key:
        return x_api_key.strip()
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return None


def require_api_key(
    raw_key: Optional[str] = Depends(get_api_key_from_headers),
    db: Session = Depends(get_db),
) -> APIKey:
    if not raw_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")

    key_hash = _hash_key(raw_key)
    row = db.query(APIKey).filter(APIKey.key_hash == key_hash, APIKey.is_active == True).first()  # noqa: E712
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    # Best-effort last_used_at update
    try:
        row.last_used_at = datetime.utcnow()
        db.commit()
    except Exception:
        db.rollback()

    return row

