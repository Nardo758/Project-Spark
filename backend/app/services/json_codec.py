import json
from typing import Any


def loads_json(value: Any, default: Any):
    """
    Robust JSON loader for "JSON stored in Text" patterns.

    - If value is None/empty -> default
    - If value is already a dict/list -> value
    - If value is a string -> parse JSON, else default on failure
    """
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return default
        try:
            return json.loads(s)
        except Exception:
            return default
    return default


def dumps_json(value: Any) -> str:
    """Serialize JSON safely (always returns a string)."""
    try:
        return json.dumps(value)
    except Exception:
        return json.dumps({})

