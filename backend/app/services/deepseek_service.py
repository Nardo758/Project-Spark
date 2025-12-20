from __future__ import annotations

import json
import os
import logging
from decimal import Decimal
from typing import Any, Dict, Tuple

import httpx
from sqlalchemy.orm import Session

from app.models.brain import Brain
from app.models.opportunity import Opportunity
from app.services.json_codec import loads_json

logger = logging.getLogger(__name__)


def _estimate_cost_usd(total_tokens: int) -> Decimal:
    """
    Cost estimate based on total tokens.
    Default: $0.001 / 1K tokens (UI-aligned; override via env).
    """
    usd_per_1k = os.getenv("DEEPSEEK_USD_PER_1K_TOKENS", "0.001")
    try:
        rate = Decimal(usd_per_1k)
    except Exception:
        rate = Decimal("0.001")
    return (Decimal(total_tokens) / Decimal(1000)) * rate


class DeepSeekService:
    """
    Minimal DeepSeek (OpenAI-compatible) integration.

    Uses:
    - POST {base_url}/v1/chat/completions
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=httpx.Timeout(20.0),
        )

    def analyze_opportunity_quick_match(self, *, brain: Brain, opp: Opportunity) -> Tuple[int, str, int]:
        """
        Returns (match_score, reasoning, total_tokens_used_for_this_call).
        """
        if not self.is_configured():
            raise RuntimeError("DeepSeek not configured (missing DEEPSEEK_API_KEY)")

        focus_tags = loads_json(brain.focus_tags, default=[])
        focus = ", ".join([t for t in focus_tags if isinstance(t, str)][:6]) or "your goals"

        system = (
            f"You are DeepSeek Brain for '{brain.name}'. "
            f"Primary focus: {focus}. "
            "Return concise, actionable output."
        )
        user = f"""Analyze this opportunity for fit and return ONLY valid JSON with keys:
- match_score: integer 0-100
- reasoning: short 1-2 sentences, no markdown

OPPORTUNITY:
Title: {opp.title}
Category: {opp.category or 'N/A'}
Description: {(opp.description or '')[:900]}
Market size: {opp.market_size or opp.ai_market_size_estimate or 'N/A'}
Validations: {opp.validation_count or 0}
"""

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "max_tokens": 300,
        }

        with self._client() as client:
            res = client.post("/v1/chat/completions", json=payload)
            data = res.json()
            if res.status_code >= 400:
                raise RuntimeError(data.get("error", {}).get("message") or f"DeepSeek error ({res.status_code})")

        content = (
            (((data or {}).get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        ).strip()
        if content.startswith("```"):
            # strip fenced block if present
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]
            content = content.replace("json", "", 1).strip()

        try:
            parsed = json.loads(content)
        except Exception as e:
            logger.warning("DeepSeek returned non-JSON content: %s", content[:300])
            raise RuntimeError("DeepSeek returned invalid JSON") from e

        match_score = int(parsed.get("match_score", 0))
        match_score = max(0, min(100, match_score))
        reasoning = str(parsed.get("reasoning", "")).strip() or "No reasoning returned."

        usage = data.get("usage") or {}
        total_tokens = int(usage.get("total_tokens") or 0)
        return match_score, reasoning, max(0, total_tokens)

    def upsert_brain_for_user(self, *, db: Session, user_id: int, name: str, focus_tags: list[str]) -> Brain:
        brain = db.query(Brain).filter(Brain.user_id == user_id).first()
        if brain:
            brain.name = name
            brain.focus_tags = json.dumps(focus_tags)
        else:
            brain = Brain(
                user_id=user_id,
                name=name,
                focus_tags=json.dumps(focus_tags),
                match_score=42,
                knowledge_items=0,
                tokens_used=0,
                estimated_cost_usd=Decimal("0"),
            )
            db.add(brain)
        db.commit()
        db.refresh(brain)
        return brain

    def get_active_brain(self, *, db: Session, user_id: int) -> Brain | None:
        return db.query(Brain).filter(Brain.user_id == user_id).first()

    def record_usage(self, *, db: Session, brain: Brain, tokens: int) -> Brain:
        if tokens <= 0:
            return brain
        brain.tokens_used = int(brain.tokens_used or 0) + int(tokens)
        brain.estimated_cost_usd = _estimate_cost_usd(int(brain.tokens_used))
        db.commit()
        db.refresh(brain)
        return brain


deepseek_service = DeepSeekService()

