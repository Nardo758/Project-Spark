from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def _client_ip(request: Request) -> Optional[str]:
    # Prefer X-Forwarded-For when present (first hop).
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else None


def log_event(
    db: Session,
    *,
    action: str,
    actor: User | None,
    actor_type: str,
    request: Request | None = None,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    metadata: Any | None = None,
) -> None:
    """
    Best-effort audit log write. Never raises.
    """
    try:
        ip = _client_ip(request) if request else None
        ua = request.headers.get("user-agent") if request else None
        metadata_json = None
        if metadata is not None:
            try:
                metadata_json = json.dumps(metadata)
            except Exception:
                metadata_json = None

        entry = AuditLog(
            actor_user_id=(actor.id if actor else None),
            actor_type=actor_type or ("admin" if (actor and getattr(actor, "is_admin", False)) else "user"),
            action=action,
            resource_type=resource_type,
            resource_id=(str(resource_id) if resource_id is not None else None),
            ip_address=ip,
            user_agent=ua,
            metadata_json=metadata_json,
        )
        db.add(entry)
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass

