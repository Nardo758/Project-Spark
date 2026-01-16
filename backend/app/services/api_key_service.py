"""
API Key Service - January 2026

Manages API keys for Business Track teams:
- Key generation with secure hashing
- Key validation and rate limiting
- Usage tracking
"""

import secrets
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.team import Team, TeamApiKey, TeamMember, TeamRole
from app.models.user import User

logger = logging.getLogger(__name__)

# Rate limit tracking (in-memory for now, could use Redis)
_rate_limit_cache: Dict[str, List[datetime]] = {}


def generate_api_key() -> Tuple[str, str, str]:
    """
    Generate a new API key.
    
    Returns:
        Tuple of (full_key, key_hash, key_prefix)
    """
    # Generate 32-byte random key
    key_bytes = secrets.token_bytes(32)
    full_key = f"og_{secrets.token_urlsafe(32)}"
    
    # Hash for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    
    # Prefix for display (first 8 chars after og_)
    key_prefix = full_key[:10]
    
    return full_key, key_hash, key_prefix


def hash_api_key(key: str) -> str:
    """Hash an API key for comparison."""
    return hashlib.sha256(key.encode()).hexdigest()


def create_api_key(
    team: Team,
    user: User,
    name: str,
    scopes: Optional[List[str]] = None,
    expires_in_days: Optional[int] = None,
    db: Session = None
) -> Tuple[bool, str, Optional[str]]:
    """
    Create a new API key for a team.
    
    Args:
        team: The team to create the key for
        user: The user creating the key
        name: A friendly name for the key
        scopes: List of allowed scopes (e.g., ["opportunities:read", "reports:read"])
        expires_in_days: Optional expiration in days
        db: Database session
        
    Returns:
        Tuple of (success, message, full_key or None)
    """
    # Check if user has permission
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team.id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not member or member.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
        return False, "You don't have permission to create API keys", None
    
    # Check if team has API access enabled
    if not team.api_enabled:
        return False, "API access is not enabled for this team", None
    
    # Generate the key
    full_key, key_hash, key_prefix = generate_api_key()
    
    # Calculate expiration
    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    # Create the key record
    api_key = TeamApiKey(
        team_id=team.id,
        name=name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        scopes=json.dumps(scopes or ["opportunities:read"]),
        expires_at=expires_at,
        created_by_id=user.id
    )
    
    db.add(api_key)
    db.commit()
    
    logger.info(f"API key created for team {team.id} by user {user.id}")
    
    # Return the full key - this is the only time it will be visible
    return True, "API key created successfully", full_key


def validate_api_key(key: str, db: Session) -> Tuple[bool, Optional[Team], Optional[TeamApiKey], str]:
    """
    Validate an API key.
    
    Returns:
        Tuple of (is_valid, team, api_key, error_message)
    """
    if not key or not key.startswith("og_"):
        return False, None, None, "Invalid API key format"
    
    key_hash = hash_api_key(key)
    
    api_key = db.query(TeamApiKey).filter(
        TeamApiKey.key_hash == key_hash
    ).first()
    
    if not api_key:
        return False, None, None, "Invalid API key"
    
    if not api_key.is_active:
        return False, None, None, "API key is disabled"
    
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        return False, None, None, "API key has expired"
    
    team = api_key.team
    
    if not team.api_enabled:
        return False, None, None, "API access is disabled for this team"
    
    # Update usage tracking
    api_key.last_used_at = datetime.utcnow()
    api_key.usage_count += 1
    db.commit()
    
    return True, team, api_key, ""


def check_rate_limit(team_id: int, rate_limit: int) -> Tuple[bool, int]:
    """
    Check if a team has exceeded their rate limit.
    
    Args:
        team_id: The team ID
        rate_limit: Requests per minute limit
        
    Returns:
        Tuple of (is_allowed, requests_remaining)
    """
    cache_key = f"team_{team_id}"
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=1)
    
    # Clean old entries and get current count
    if cache_key in _rate_limit_cache:
        _rate_limit_cache[cache_key] = [
            ts for ts in _rate_limit_cache[cache_key]
            if ts > window_start
        ]
        current_count = len(_rate_limit_cache[cache_key])
    else:
        _rate_limit_cache[cache_key] = []
        current_count = 0
    
    if current_count >= rate_limit:
        return False, 0
    
    # Add this request
    _rate_limit_cache[cache_key].append(now)
    
    return True, rate_limit - current_count - 1


def revoke_api_key(key_id: int, user: User, db: Session) -> Tuple[bool, str]:
    """Revoke (disable) an API key."""
    api_key = db.query(TeamApiKey).filter(TeamApiKey.id == key_id).first()
    
    if not api_key:
        return False, "API key not found"
    
    # Check permission
    member = db.query(TeamMember).filter(
        TeamMember.team_id == api_key.team_id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not member or member.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
        return False, "You don't have permission to revoke this key"
    
    api_key.is_active = False
    db.commit()
    
    logger.info(f"API key {key_id} revoked by user {user.id}")
    return True, "API key revoked successfully"


def list_api_keys(team_id: int, db: Session) -> List[Dict[str, Any]]:
    """List all API keys for a team (without revealing the actual keys)."""
    keys = db.query(TeamApiKey).filter(
        TeamApiKey.team_id == team_id
    ).order_by(TeamApiKey.created_at.desc()).all()
    
    return [
        {
            "id": k.id,
            "name": k.name,
            "key_prefix": k.key_prefix,
            "is_active": k.is_active,
            "scopes": json.loads(k.scopes) if k.scopes else [],
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            "usage_count": k.usage_count,
            "expires_at": k.expires_at.isoformat() if k.expires_at else None,
            "created_at": k.created_at.isoformat() if k.created_at else None,
        }
        for k in keys
    ]


def enable_team_api_access(team: Team, rate_limit: int = 100, db: Session = None) -> bool:
    """Enable API access for a team."""
    team.api_enabled = True
    team.api_rate_limit = rate_limit
    db.commit()
    logger.info(f"API access enabled for team {team.id}")
    return True


def disable_team_api_access(team: Team, db: Session) -> bool:
    """Disable API access for a team."""
    team.api_enabled = False
    db.commit()
    logger.info(f"API access disabled for team {team.id}")
    return True
