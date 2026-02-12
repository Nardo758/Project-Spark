"""
🛡️ OppGrid AI Agent Security Protocols
Comprehensive data protection and access control system
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from cryptography.fernet import Fernet
# import redis.asyncio as redis  # Optional - for rate limiting
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

class SubscriptionTier(Enum):
    FREE = "free"
    PRO = "pro" 
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

class AgentAction(Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ANALYZE = "analyze"
    WEBHOOK = "webhook"

# Subscription-based access control matrix
AGENT_ACCESS_MATRIX = {
    SubscriptionTier.FREE.value: {
        "opportunities": {
            "read": {"limit": 10, "fields": ["title", "description", "category", "feasibility_score"]},
            "create": False,
            "update": False,
            "delete": False
        },
        "ai_analysis": {
            "enabled": False,
            "daily_limit": 0,
            "max_tokens": 0,
            "rate_limit": "0/minute"
        },
        "agents": {
            "install": False,
            "create": False,
            "custom_webhooks": False,
            "marketplace": {"browse": True, "install": False}
        }
    },
    SubscriptionTier.PRO.value: {
        "opportunities": {
            "read": {"limit": 100, "fields": "all"},
            "create": {"daily": 5, "requires_approval": False},
            "update": {"own_only": True},
            "delete": {"own_only": True}
        },
        "ai_analysis": {
            "enabled": True,
            "daily_limit": 50,
            "max_tokens": 10000,
            "rate_limit": "10/minute"
        },
        "agents": {
            "install": {"marketplace_only": True, "max": 5},
            "create": False,
            "custom_webhooks": False,
            "marketplace": {"browse": True, "install": True}
        }
    },
    SubscriptionTier.BUSINESS.value: {
        "opportunities": {
            "read": {"limit": 500, "fields": "all"},
            "create": {"daily": 20, "team_based": True},
            "update": {"team_based": True},
            "delete": {"team_based": True}
        },
        "ai_analysis": {
            "enabled": True,
            "daily_limit": 200,
            "max_tokens": 50000,
            "rate_limit": "30/minute"
        },
        "agents": {
            "install": {"marketplace + custom": True, "max": 10},
            "create": {"max": 3},
            "custom_webhooks": True,
            "marketplace": {"browse": True, "install": True, "create": True}
        }
    },
    SubscriptionTier.ENTERPRISE.value: {
        "opportunities": {
            "read": {"unlimited": True, "fields": "all"},
            "create": {"unlimited": True},
            "update": {"team_based": True},
            "delete": {"team_based": True}
        },
        "ai_analysis": {
            "enabled": True,
            "unlimited": True,
            "rate_limit": "100/minute"
        },
        "agents": {
            "install": {"unlimited": True},
            "create": {"unlimited": True},
            "custom_webhooks": True,
            "marketplace": {"browse": True, "install": True, "create": True},
            "private_agents": True
        }
    }
}

# Field-level security restrictions
FIELD_RESTRICTIONS = {
    SubscriptionTier.FREE.value: {
        "opportunities": {
            "excluded_fields": [
                "detailed_analysis", "competitor_data", "market_size_details",
                "expert_contacts", "private_notes", "validation_history",
                "ai_confidence_scores", "proprietary_metrics", "revenue_projections"
            ],
            "masked_fields": {
                "contact_email": "***@***.com",
                "location": "City, Country",
                "estimated_value": "Contact for details"
            }
        }
    },
    SubscriptionTier.PRO.value: {
        "opportunities": {
            "excluded_fields": [
                "expert_contacts", "private_notes", "internal_scoring"
            ],
            "masked_fields": {
                "contact_email": "partial_mask",
                "estimated_value": "Range provided"
            }
        }
    }
}

class AgentCapabilityToken:
    """Manages agent permissions and capabilities based on user subscription"""
    
    def __init__(self, user_id: str, subscription_tier: str, agent_id: str, 
                 requested_capabilities: Dict[str, Any], redis_client=None):
        self.user_id = user_id
        self.subscription_tier = subscription_tier
        self.agent_id = agent_id
        self.redis_client = redis_client
        self.requested_capabilities = requested_capabilities
        self.capabilities = self._validate_and_filter_capabilities()
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(hours=1)
        self.token_id = f"act_{user_id}_{agent_id}_{int(time.time())}"
        
    def _validate_and_filter_capabilities(self) -> Dict[str, Any]:
        """Filter requested capabilities based on subscription tier"""
        if self.subscription_tier not in AGENT_ACCESS_MATRIX:
            raise ValueError(f"Invalid subscription tier: {self.subscription_tier}")
            
        allowed_capabilities = {}
        tier_config = AGENT_ACCESS_MATRIX[self.subscription_tier]
        
        for capability, config in self.requested_capabilities.items():
            if capability in tier_config["agents"]:
                tier_capability = tier_config["agents"][capability]
                
                if tier_capability is True:
                    allowed_capabilities[capability] = config
                elif isinstance(tier_capability, dict):
                    # Apply tier-specific limits
                    allowed_capabilities[capability] = self._apply_tier_limits(capability, config, tier_capability)
                    
        return allowed_capabilities
    
    def _apply_tier_limits(self, capability: str, agent_config: Dict[str, Any], 
                          tier_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply subscription-based limits to specific capabilities"""
        
        # Check agent creation limits
        if capability == "create" and "max" in tier_config:
            current_count = self._get_user_agent_count()
            if current_count >= tier_config["max"]:
                raise PermissionError(f"Agent creation limit reached for {self.subscription_tier} tier")
                
        return {
            **agent_config,
            "tier_limits": tier_config,
            "enforced": True,
            "subscription_tier": self.subscription_tier
        }
    
    def _get_user_agent_count(self) -> int:
        """Get current number of agents for this user"""
        # This would query the database
        # For now, return 0 (implementation depends on your DB layer)
        return 0
    
    def can_perform_action(self, action: str, resource_type: str) -> bool:
        """Check if agent can perform specific action on resource type"""
        
        # Check if action is allowed for this subscription tier
        if resource_type not in AGENT_ACCESS_MATRIX[self.subscription_tier]:
            return False
            
        resource_config = AGENT_ACCESS_MATRIX[self.subscription_tier][resource_type]
        
        if action not in resource_config:
            return False
            
        action_config = resource_config[action]
        
        # Handle boolean permissions
        if isinstance(action_config, bool):
            return action_config
            
        # Handle dict permissions with limits
        if isinstance(action_config, dict):
            return self._check_action_limits(action, action_config)
            
        return False
    
    def _check_action_limits(self, action: str, action_config: Dict[str, Any]) -> bool:
        """Check if action is within subscription limits"""
        
        # Check daily limits
        if "daily_limit" in action_config:
            current_usage = self._get_daily_usage(action)
            if current_usage >= action_config["daily_limit"]:
                return False
                
        # Check rate limits
        if "rate_limit" in action_config:
            if not self._check_rate_limit(action):
                return False
                
        return True
    
    def _get_daily_usage(self, action: str) -> int:
        """Get current daily usage for specific action"""
        if not self.redis_client:
            return 0
            
        today = datetime.utcnow().date().isoformat()
        key = f"usage:{self.user_id}:{action}:{today}"
        
        try:
            usage = self.redis_client.get(key)
            return int(usage) if usage else 0
        except:
            return 0
    
    def _check_rate_limit(self, action: str) -> bool:
        """Check rate limiting for specific action"""
        if not self.redis_client:
            return True
            
        # Simple sliding window rate limiting
        key = f"rate_limit:{self.user_id}:{self.agent_id}:{action}"
        current_count = self.redis_client.incr(key)
        
        if current_count == 1:
            # Set expiry for sliding window (1 minute default)
            self.redis_client.expire(key, 60)
            
        # Check against limit (10 requests per minute default)
        return current_count <= 10
    
    def get_remaining_quota(self, action: str) -> Dict[str, int]:
        """Get remaining quota for specific actions"""
        
        if action not in AGENT_ACCESS_MATRIX[self.subscription_tier]:
            return {"daily": 0, "total": 0}
            
        action_config = AGENT_ACCESS_MATRIX[self.subscription_tier][action]
        
        if isinstance(action_config, dict) and "daily_limit" in action_config:
            current_usage = self._get_daily_usage(action)
            remaining = max(0, action_config["daily_limit"] - current_usage)
            
            return {
                "daily": remaining,
                "total": action_config["daily_limit"],
                "used_today": current_usage
            }
            
        return {"daily": 0, "total": 0, "used_today": 0}

class DataAccessFilter:
    """Filters data fields based on subscription tier and security requirements"""
    
    @staticmethod
    def filter_data_for_tier(data: Dict[str, Any], tier: str, data_type: str) -> Dict[str, Any]:
        """Remove restricted fields based on subscription tier"""
        
        if tier not in FIELD_RESTRICTIONS or data_type not in FIELD_RESTRICTIONS[tier]:
            return data
            
        restrictions = FIELD_RESTRICTIONS[tier][data_type]
        filtered_data = data.copy()
        
        # Remove excluded fields
        for field in restrictions.get("excluded_fields", []):
            if field in filtered_data:
                del filtered_data[field]
        
        # Mask sensitive fields
        for field, mask in restrictions.get("masked_fields", {}).items():
            if field in filtered_data:
                if mask == "partial_mask":
                    filtered_data[field] = DataAccessFilter._apply_partial_mask(filtered_data[field])
                elif mask == "full_mask":
                    filtered_data[field] = "***"
                else:
                    filtered_data[field] = mask
        
        return filtered_data
    
    @staticmethod
    def _apply_partial_mask(value: str) -> str:
        """Apply partial masking to sensitive data"""
        if "@" in value:  # Email
            parts = value.split("@")
            return f"{parts[0][0]}***@{parts[1]}"
        elif len(value) > 4:  # General text
            return f"{value[:2]}***{value[-2:]}"
        else:
            return "***"

class AgentRateLimiter:
    """Sophisticated rate limiting for AI agents"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        # Handle case where Redis is not available
        if redis_client is None and not REDIS_AVAILABLE:
            self.redis_client = None
        
    async def check_rate_limit(self, user_id: str, agent_id: str, action: str) -> tuple[bool, str]:
        """Check if agent action is within rate limits"""
        
        if not self.redis_client:
            return True, "No rate limiting configured (Redis not available)"
        
        # Multi-tier rate limiting
        rate_limits = {
            "user_agent": f"rate:agent:{user_id}:{agent_id}:{action}",
            "user_global": f"rate:user:{user_id}:all_agents:{action}", 
            "action_global": f"rate:action:{action}:all_users"
        }
        
        # Check each limit
        for limit_type, key in rate_limits.items():
            allowed, message = await self._check_specific_limit(key, action, limit_type)
            if not allowed:
                return False, f"Rate limit exceeded: {limit_type} - {message}"
        
        return True, "Within limits"
    
    async def _check_specific_limit(self, key: str, action: str, limit_type: str) -> tuple[bool, str]:
        """Check specific rate limit with sliding window"""
        
        if not self.redis_client:
            return True, "No Redis configured"
        
        # Get limits based on type and action
        window_size = self._get_window_size(limit_type, action)
        max_requests = self._get_max_requests(limit_type, action)
        
        current_count = await self.redis_client.incr(key)
        if current_count == 1:
            await self.redis_client.expire(key, window_size)
        
        if current_count > max_requests:
            return False, f"Limit: {max_requests} requests per {window_size}s"
        
        return True, f"OK ({current_count}/{max_requests})"
    
    def _get_window_size(self, limit_type: str, action: str) -> int:
        """Get rate limit window size in seconds"""
        windows = {
            "user_agent": 60,      # 1 minute
            "user_global": 300,    # 5 minutes  
            "action_global": 60    # 1 minute
        }
        return windows.get(limit_type, 60)
    
    def _get_max_requests(self, limit_type: str, action: str) -> int:
        """Get maximum requests per window"""
        limits = {
            "user_agent": 10,      # 10 requests per minute per agent
            "user_global": 50,     # 50 requests per 5 minutes per user
            "action_global": 100   # 100 requests per minute for action
        }
        return limits.get(limit_type, 10)

class AgentAuditLogger:
    """Comprehensive audit logging for agent activities"""
    
    def __init__(self, db_session, redis_client=None):
        self.db = db_session
        self.redis = redis_client
        
    async def log_agent_access(self, user_id: str, agent_id: str, action: str, 
                             data_accessed: Dict[str, Any], success: bool = True) -> None:
        """Log every agent data access attempt"""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "agent_id": agent_id,
            "action": action,
            "data_accessed": self._sanitize_data_for_audit(data_accessed),
            "data_size": len(str(data_accessed)),
            "success": success,
            "ip_address": self._get_client_ip(),
            "subscription_tier": await self._get_user_tier(user_id),
            "rate_limit_consumed": await self._get_rate_limit_usage(user_id, agent_id)
        }
        
        # Store in audit log
        await self._store_audit_log(audit_entry)
        
        # Check for suspicious activity
        if self._is_suspicious_activity(audit_entry):
            await self._send_security_alert(audit_entry)
    
    def _sanitize_data_for_audit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from audit logs"""
        sensitive_fields = ["password", "token", "api_key", "secret", "webhook_url"]
        
        sanitized = {}
        for key, value in data.items():
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = str(value)[:100]  # Truncate for audit
        
        return sanitized
    
    def _is_suspicious_activity(self, audit_entry: Dict[str, Any]) -> bool:
        """Detect suspicious agent behavior patterns"""
        
        suspicious_patterns = [
            # High frequency access
            audit_entry.get("rate_limit_consumed", 0) > 0.8,
            
            # Large data downloads (>1MB)
            audit_entry.get("data_size", 0) > 1000000,
            
            # Repeated failed attempts
            audit_entry.get("success") is False,
            
            # Accessing restricted data types
            any(field in str(audit_entry.get("data_accessed", "")) 
                for field in ["api_keys", "webhook_urls", "authentication_tokens"])
        ]
        
        return any(suspicious_patterns)
    
    async def _send_security_alert(self, audit_entry: Dict[str, Any]) -> None:
        """Send security alert for suspicious activity"""
        # Implementation would send to security team/admin
        print(f"🚨 SECURITY ALERT: Suspicious agent activity detected")
        print(f"User: {audit_entry['user_id']}, Agent: {audit_entry['agent_id']}")
        print(f"Action: {audit_entry['action']}, Success: {audit_entry['success']}")
    
    def _get_client_ip(self) -> str:
        """Get client IP address (implementation depends on framework)"""
        # This would integrate with your web framework
        return "0.0.0.0"  # Placeholder
    
    async def _get_user_tier(self, user_id: str) -> str:
        """Get user's subscription tier (implementation depends on your user system)"""
        # This would query your user database
        return SubscriptionTier.PRO.value  # Placeholder
    
    async def _get_rate_limit_usage(self, user_id: str, agent_id: str) -> float:
        """Get current rate limit usage percentage"""
        if not self.redis:
            return 0.0
        
        # Implementation would check Redis for rate limit usage
        return 0.0  # Placeholder
    
    async def _store_audit_log(self, audit_entry: Dict[str, Any]) -> None:
        """Store audit log in database"""
        # Implementation would store in your audit log table
        print(f"📊 AUDIT: {audit_entry['user_id']} - {audit_entry['agent_id']} - {audit_entry['action']}")

class DataBreachPrevention:
    """Prevents and detects potential data breaches"""
    
    async def prevent_bulk_data_extraction(self, user_id: str, agent_id: str, 
                                         requested_data: Dict[str, Any]) -> tuple[bool, str]:
        """Prevent agents from bulk downloading data"""
        
        # Check request size
        data_size = len(str(requested_data))
        if data_size > 1000000:  # 1MB threshold
            return False, "Large data request detected - requires approval"
        
        # Check for scraping patterns
        recent_requests = await self._get_recent_agent_requests(user_id, agent_id, hours=1)
        similar_requests = [req for req in recent_requests 
                          if self._requests_are_similar(req, requested_data)]
        
        if len(similar_requests) > 5:  # Potential scraping
            return False, "Scraping pattern detected - access blocked"
        
        # Check for cross-user data requests
        if self._requests_cross_user_boundary(requested_data):
            return False, "Cross-user data access not allowed"
        
        return True, "Access approved"
    
    async def _get_recent_agent_requests(self, user_id: str, agent_id: str, hours: int) -> List[Dict[str, Any]]:
        """Get recent agent requests for pattern analysis"""
        # Implementation would query audit logs
        return []
    
    def _requests_are_similar(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """Check if two requests are similar (potential scraping)"""
        # Simple similarity check - can be enhanced
        return str(req1) == str(req2)
    
    def _requests_cross_user_boundary(self, requested_data: Dict[str, Any]) -> bool:
        """Check if request accesses data across user boundaries"""
        # Implementation would check for cross-user data access
        return False

# Security service integration
class AgentSecurityService:
    """Main security service for AI agents"""
    
    def __init__(self, db_session, redis_client=None, encryption_key=None):
        self.db = db_session
        self.redis = redis_client
        self.encryption_key = encryption_key or Fernet.generate_key()
        
        # Initialize security components
        self.rate_limiter = AgentRateLimiter(redis_client)
        self.data_filter = DataAccessFilter()
        self.data_protector = SensitiveDataProtector(self.encryption_key)
        self.audit_logger = AgentAuditLogger(db_session, redis_client)
        self.breach_prevention = DataBreachPrevention()
    
    async def process_agent_request(self, user_id: str, agent_id: str, action: str, 
                                  requested_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main security checkpoint for all agent requests"""
        
        try:
            # 1. Verify subscription and permissions
            user_tier = await self._get_user_subscription_tier(user_id)
            
            # 2. Check if action is allowed
            if not self._can_agent_perform_action(user_id, agent_id, action):
                raise PermissionError("Action not allowed for this subscription tier")
            
            # 3. Apply rate limiting
            rate_limit_ok, rate_limit_message = await self.rate_limiter.check_rate_limit(
                user_id, agent_id, action
            )
            if not rate_limit_ok:
                await self.audit_logger.log_agent_access(
                    user_id, agent_id, action, requested_data, success=False
                )
                raise RateLimitError(rate_limit_message)
            
            # 4. Prevent bulk data extraction
            access_allowed, access_message = await self.breach_prevention.prevent_bulk_data_extraction(
                user_id, agent_id, requested_data
            )
            if not access_allowed:
                await self.audit_logger.log_agent_access(
                    user_id, agent_id, action, requested_data, success=False
                )
                raise DataAccessError(access_message)
            
            # 5. Filter data based on subscription tier
            filtered_data = self.data_filter.filter_data_for_tier(
                requested_data, user_tier, "opportunities"
            )
            
            # 6. Apply usage limits
            filtered_data = await self._apply_usage_limits(filtered_data, user_tier, action)
            
            # 7. Create audit trail
            await self.audit_logger.log_agent_access(
                user_id, agent_id, action, filtered_data, success=True
            )
            
            return filtered_data
            
        except Exception as e:
            # Log security errors
            await self.audit_logger.log_agent_access(
                user_id, agent_id, action, requested_data, success=False
            )
            raise e
    
    async def _get_user_subscription_tier(self, user_id: str) -> str:
        """Get user's subscription tier (implementation depends on your user system)"""
        # This would query your user database
        # For now, return PRO as default
        return SubscriptionTier.PRO.value
    
    def _can_agent_perform_action(self, user_id: str, agent_id: str, action: str) -> bool:
        """Check if agent can perform specific action"""
        # Create temporary token to check permissions
        token = AgentCapabilityToken(
            user_id=user_id,
            subscription_tier=self._get_user_subscription_tier(user_id),
            agent_id=agent_id,
            requested_capabilities={action: {}},
            redis_client=self.redis
        )
        
        return token.can_perform_action(action, "opportunities")
    
    async def _apply_usage_limits(self, data: Dict[str, Any], tier: str, action: str) -> Dict[str, Any]:
        """Apply subscription-based usage limits"""
        
        # Limit number of records returned based on tier
        if "opportunities" in data and isinstance(data["opportunities"], list):
            tier_config = AGENT_ACCESS_MATRIX[tier]["opportunities"]["read"]
            if isinstance(tier_config, dict) and "limit" in tier_config:
                limit = tier_config["limit"]
                if len(data["opportunities"]) > limit:
                    data["opportunities"] = data["opportunities"][:limit]
                    data["usage_warning"] = f"Results limited to {limit} items per subscription tier"
        
        return data

# Security exceptions
class SecurityError(Exception):
    """Base security exception"""
    pass

class PermissionError(SecurityError):
    """Permission denied"""
    pass

class RateLimitError(SecurityError):
    """Rate limit exceeded"""
    pass

class DataAccessError(SecurityError):
    """Data access denied"""
    pass