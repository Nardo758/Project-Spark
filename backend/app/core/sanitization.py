"""
Input sanitization helpers for user-supplied data.

Use these at API boundaries to reduce XSS risk when data is stored or echoed.
"""

from __future__ import annotations

import html
from typing import Any, Optional


def sanitize_text(value: Optional[str], *, max_length: Optional[int] = None) -> Optional[str]:
    """Escape HTML and trim whitespace for user-provided strings."""
    if value is None:
        return None
    cleaned = html.escape(value).strip()
    if max_length is not None:
        cleaned = cleaned[: max(0, int(max_length))]
    return cleaned


def sanitize_json(value: Any, *, max_str_length: int = 2000) -> Any:
    """Recursively sanitize string values within JSON-like payloads."""
    if isinstance(value, str):
        return sanitize_text(value, max_length=max_str_length) or ""
    if isinstance(value, list):
        return [sanitize_json(item, max_str_length=max_str_length) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_json(val, max_str_length=max_str_length) for key, val in value.items()}
    return value
