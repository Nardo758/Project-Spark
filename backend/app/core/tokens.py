"""
Token generation and validation utilities
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional


def generate_verification_token() -> str:
    """
    Generate a secure random token for email verification

    Returns:
        str: A URL-safe random token
    """
    return secrets.token_urlsafe(32)


def generate_password_reset_token() -> str:
    """
    Generate a secure random token for password reset

    Returns:
        str: A URL-safe random token
    """
    return secrets.token_urlsafe(32)


def get_verification_token_expiry(hours: int = 24) -> datetime:
    """
    Get expiration time for verification token

    Args:
        hours: Number of hours until expiration (default: 24)

    Returns:
        datetime: Expiration timestamp
    """
    return datetime.utcnow() + timedelta(hours=hours)


def get_password_reset_token_expiry(hours: int = 1) -> datetime:
    """
    Get expiration time for password reset token

    Args:
        hours: Number of hours until expiration (default: 1)

    Returns:
        datetime: Expiration timestamp
    """
    return datetime.utcnow() + timedelta(hours=hours)


def is_token_expired(expiry_time: Optional[datetime]) -> bool:
    """
    Check if a token has expired

    Args:
        expiry_time: Token expiration timestamp

    Returns:
        bool: True if token is expired or None, False otherwise
    """
    if expiry_time is None:
        return True
    return datetime.utcnow() > expiry_time
