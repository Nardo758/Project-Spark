from __future__ import annotations

import logging
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_cost import AICost

logger = logging.getLogger(__name__)


def _compute_cost(provider: str, total_tokens: Optional[int]) -> Optional[float]:
    if total_tokens is None:
        return None
    rate = None
    if provider == "claude":
        rate = settings.CLAUDE_COST_PER_1K_TOKENS
    elif provider == "deepseek":
        rate = settings.DEEPSEEK_COST_PER_1K_TOKENS
    if rate is None:
        return None
    try:
        return round((float(total_tokens) * float(rate)) / 1000.0, 4)
    except Exception:
        return None


def record_ai_cost(
    db: Session,
    *,
    user_id: Optional[int],
    provider: str,
    endpoint: str,
    task_type: Optional[str] = None,
    usage: Optional[Dict[str, Any]] = None,
) -> None:
    if not provider:
        return
    if not usage:
        return

    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    total_tokens = usage.get("total_tokens")
    if total_tokens is None and isinstance(input_tokens, int) and isinstance(output_tokens, int):
        total_tokens = input_tokens + output_tokens

    if total_tokens is None:
        return

    cost_usd = _compute_cost(provider, total_tokens)

    try:
        row = AICost(
            user_id=user_id,
            provider=provider,
            endpoint=endpoint,
            task_type=task_type,
            input_tokens=input_tokens if isinstance(input_tokens, int) else None,
            output_tokens=output_tokens if isinstance(output_tokens, int) else None,
            total_tokens=total_tokens if isinstance(total_tokens, int) else None,
            cost_usd=cost_usd,
        )
        db.add(row)
        db.commit()
    except Exception as exc:
        logger.warning("Failed to record AI cost: %s", exc)
        try:
            db.rollback()
        except Exception:
            pass
