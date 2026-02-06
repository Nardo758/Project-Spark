# 🔒 OppGrid AI Agent Security Protocols
# Data Protection & Access Control Framework

## 🛡️ Security Architecture Overview

### Core Principle: **Principle of Least Privilege + Subscription-Based Access**
Every AI agent operates under strict access controls tied to user subscription levels with comprehensive audit trails.

---

## 📋 Agent Security Protocols

### 1. **Subscription-Based Access Control (SBAC)**

#### Access Matrix by Subscription Tier

```python
AGENT_ACCESS_MATRIX = {
    "free": {
        "opportunities": {
            "read": {"limit": 10, "fields": ["title", "description", "category"]},
            "create": False,
            "update": False,
            "delete": False
        },
        "ai_analysis": {
            "enabled": False,
            "daily_limit": 0,
            "max_tokens": 0
        },
        "agents": {
            "install": False,
            "create": False,
            "custom_webhooks": False
        }
    },
    "pro": {
        "opportunities": {
            "read": {"limit": 100, "fields": "all"},
            "create": {"daily": 5},
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
            "install": {"marketplace_only": True},
            "create": False,
            "custom_webhooks": False
        }
    },
    "business": {
        "opportunities": {
            "read": {"limit": 500, "fields": "all"},
            "create": {"daily": 20},
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
            "install": {"marketplace + custom": True},
            "create": {"max": 3},
            "custom_webhooks": True
        }
    },
    "enterprise": {
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
            "private_agents": True
        }
    }
}
```

---

### 2. **Agent Permission Framework**

#### Agent Capability Tokens (ACT)
```python
class AgentCapabilityToken:
    def __init__(self, user_id, subscription_tier, agent_id, capabilities):
        self.user_id = user_id
        self.subscription_tier = subscription_tier
        self.agent_id = agent_id
        self.capabilities = self._validate_capabilities(capabilities)
        self.expires_at = datetime.utcnow() + timedelta(hours=1)
        self.rate_limit_key = f"agent_rate:{user_id}:{agent_id}"
        
    def _validate_capabilities(self, requested_capabilities):
        """Filter capabilities based on subscription tier"""
        allowed = {}
        user_tier = self.subscription_tier
        
        for capability, config in requested_capabilities.items():
            if capability in AGENT_ACCESS_MATRIX[user_tier]["agents"]:
                # Check if capability is enabled for this tier
                tier_config = AGENT_ACCESS_MATRIX[user_tier]["agents"][capability]
                if tier_config is True or isinstance(tier_config, dict):
                    allowed[capability] = self._apply_tier_limits(capability, config, tier_config)
        
        return allowed
    
    def _apply_tier_limits(self, capability, agent_config, tier_config):
        """Apply subscription-based limits to agent capabilities"""
        if isinstance(tier_config, dict) and "max" in tier_config:
            # Limit number of agents user can create
            current_count = self._get_user_agent_count()
            if current_count >= tier_config["max"]:
                raise PermissionError(f"Agent limit reached for {self.subscription_tier} tier")
        
        return {
            **agent_config,
            "tier_limits": tier_config,
            "enforced": True
        }
```

---

### 3. **Data Access Control Layers**

#### Layer 1: Field-Level Filtering
```python
class DataAccessFilter:
    """Filters data fields based on subscription tier"""
    
    FIELD_RESTRICTIONS = {
        "free": {
            "opportunities": {
                "excluded_fields": [
                    "detailed_analysis",
                    "competitor_data", 
                    "market_size_details",
                    "expert_contacts",
                    "private_notes",
                    "validation_history",
                    "ai_confidence_scores"
                ],
                "masked_fields": {
                    "contact_email": "***@***.com",
                    "location": "City, Country"
                }
            }
        },
        "pro": {
            "opportunities": {
                "excluded_fields": [
                    "expert_contacts",
                    "private_notes"
                ],
                "masked_fields": {
                    "contact_email": "partial_mask"
                }
            }
        }
    }
    
    @staticmethod
    def filter_data_for_tier(data, tier, data_type):
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
                filtered_data[field] = mask
        
        return filtered_data
```

---

### 4. **Rate Limiting & Throttling**

```python
class AgentRateLimiter:
    """Sophisticated rate limiting for AI agents"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def check_rate_limit(self, user_id, agent_id, action):
        """Check if agent action is within rate limits"""
        
        # Multi-tier rate limiting
        rate_limits = {
            "user_agent": f"rate:agent:{user_id}:{agent_id}",
            "user_global": f"rate:user:{user_id}:all_agents", 
            "agent_global": f"rate:agent:{agent_id}:all_users",
            "subscription_tier": f"rate:tier:{self.get_user_tier(user_id)}"
        }
        
        # Check each limit
        for limit_type, key in rate_limits.items():
            if not await self._check_specific_limit(key, action, limit_type):
                return False, f"Rate limit exceeded: {limit_type}"
        
        return True, "Within limits"
    
    async def _check_specific_limit(self, key, action, limit_type):
        """Check specific rate limit with sliding window"""
        
        # Sliding window rate limiting
        window_size = self._get_window_size(limit_type, action)
        max_requests = self._get_max_requests(limit_type, action)
        
        current_count = await self.redis.incr(key)
        if current_count == 1:
            await self.redis.expire(key, window_size)
        
        return current_count <= max_requests
```

---

### 5. **Data Encryption & Tokenization**

```python
class SensitiveDataProtector:
    """Encrypts and tokenizes sensitive data"""
    
    def __init__(self, encryption_key):
        self.fernet = Fernet(encryption_key)
        
    def protect_sensitive_fields(self, data, sensitivity_level):
        """Encrypt sensitive data fields based on sensitivity"""
        
        sensitivity_mapping = {
            "low": [],
            "medium": ["contact_info", "location_details"],
            "high": ["financial_data", "proprietary_info", "expert_contacts"],
            "critical": ["api_keys", "webhook_urls", "authentication_tokens"]
        }
        
        fields_to_protect = sensitivity_mapping.get(sensitivity_level, [])
        
        for field in fields_to_protect:
            if field in data:
                # Encrypt the field
                encrypted_value = self.fernet.encrypt(str(data[field]).encode())
                data[field] = f"encrypted:{encrypted_value.decode()}"
        
        return data
    
    def create_data_token(self, original_data, scope, expiry_hours=24):
        """Create time-limited data access token"""
        
        token_data = {
            "data_hash": hashlib.sha256(str(original_data).encode()).hexdigest(),
            "scope": scope,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat(),
            "access_level": "read_only"  # Agents get read-only by default
        }
        
        return self.fernet.encrypt(json.dumps(token_data).encode()).decode()
```

---

### 6. **Audit Trail & Monitoring**

```python
class AgentAuditLogger:
    """Comprehensive audit logging for agent activities"""
    
    async def log_agent_access(self, user_id, agent_id, action, data_accessed, success=True):
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
            "subscription_tier": self.get_user_tier(user_id),
            "rate_limit_consumed": await self._get_rate_limit_usage(user_id, agent_id)
        }
        
        # Store in audit log (separate database/table)
        await self._store_audit_log(audit_entry)
        
        # Real-time monitoring alert for suspicious activity
        if self._is_suspicious_activity(audit_entry):
            await self._send_security_alert(audit_entry)
    
    def _is_suspicious_activity(self, audit_entry):
        """Detect suspicious agent behavior patterns"""
        
        suspicious_patterns = [
            # High frequency access
            audit_entry.get("rate_limit_consumed", 0) > 0.8,
            
            # Large data downloads
            audit_entry.get("data_size", 0) > 1000000,  # 1MB
            
            # Repeated failed attempts
            audit_entry.get("success") is False and audit_entry.get("retry_count", 0) > 5,
            
            # Accessing restricted data types
            any(field in str(audit_entry.get("data_accessed", "")) 
                for field in ["api_keys", "webhook_urls", "authentication_tokens"])
        ]
        
        return any(suspicious_patterns)
```

---

### 7. **Dynamic Permission System**

```python
class DynamicPermissionManager:
    """Manages permissions that can be updated in real-time"""
    
    async def update_agent_permissions(self, user_id, agent_id, new_permissions):
        """Update agent permissions with audit trail"""
        
        # Get current permissions
        old_permissions = await self.get_agent_permissions(user_id, agent_id)
        
        # Validate new permissions against subscription tier
        validated_permissions = await self._validate_against_tier(
            user_id, new_permissions
        )
        
        # Apply changes with version control
        permission_version = {
            "user_id": user_id,
            "agent_id": agent_id,
            "old_permissions": old_permissions,
            "new_permissions": validated_permissions,
            "changed_by": "system_admin",  # Or actual admin user
            "change_reason": "subscription_upgrade",
            "timestamp": datetime.utcnow().isoformat(),
            "effective_immediately": False,  # Grace period for changes
            "grace_period_ends": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Store permission change
        await self._store_permission_version(permission_version)
        
        # Notify affected agents (graceful degradation)
        await self._notify_agents_of_permission_change(agent_id, permission_version)
        
        return True, "Permissions updated with 1-hour grace period"
```

---

### 8. **Agent Isolation & Sandboxing**

```python
class AgentIsolationManager:
    """Isolates agents to prevent data leakage between users"""
    
    def create_agent_sandbox(self, agent_id, user_id):
        """Create isolated environment for agent execution"""
        
        sandbox_config = {
            "agent_id": agent_id,
            "user_id": user_id,
            "isolated_data_scope": f"user_{user_id}_agent_{agent_id}",
            "allowed_endpoints": self._get_allowed_endpoints(user_id),
            "data_retention_hours": 24,
            "max_concurrent_requests": 5,
            "memory_limit_mb": 512,
            "timeout_seconds": 30
        }
        
        return sandbox_config
    
    def _get_allowed_endpoints(self, user_id):
        """Get API endpoints this user/agent can access"""
        
        tier = self.get_user_tier(user_id)
        
        base_endpoints = [
            "/api/opportunities",
            "/api/categories", 
            "/api/health"
        ]
        
        tier_endpoints = {
            "free": [],
            "pro": [
                "/api/opportunities/create",
                "/api/ai/analyze",
                "/api/research/basic"
            ],
            "business": [
                "/api/opportunities/team",
                "/api/ai/advanced",
                "/api/research/comprehensive",
                "/api/experts/browse"
            ],
            "enterprise": [
                "/api/opportunities/export",
                "/api/ai/custom",
                "/api/research/deep",
                "/api/experts/hire"
            ]
        }
        
        return base_endpoints + tier_endpoints.get(tier, [])
```

---

### 9. **Data Breach Prevention**

```python
class DataBreachPrevention:
    """Prevents and detects potential data breaches"""
    
    async def prevent_bulk_data_extraction(self, user_id, agent_id, requested_data):
        """Prevent agents from bulk downloading data"""
        
        # Check request patterns
        if len(requested_data) > 1000:  # Large dataset request
            await self._require_additional_approval(user_id, agent_id, requested_data)
            
        # Check for repeated similar requests (data scraping)
        recent_requests = await self._get_recent_agent_requests(user_id, agent_id, hours=1)
        
        similar_requests = [req for req in recent_requests 
                          if self._requests_are_similar(req, requested_data)]
        
        if len(similar_requests) > 5:  # Potential scraping
            await self._trigger_scraping_prevention(user_id, agent_id)
            
        # Check for cross-user data requests
        if self._requests_cross_user_boundary(requested_data):
            await self._block_cross_user_access(user_id, agent_id)
    
    async def _trigger_scraping_prevention(self, user_id, agent_id):
        """Implement scraping prevention measures"""
        
        measures = [
            # Add artificial delays
            await asyncio.sleep(2),
            
            # Insert decoy data
            decoy_data = self._generate_decoy_data()
            
            # Rate limit more aggressively
            await self._apply_emergency_rate_limit(user_id, agent_id),
            
            # Log for investigation
            await self._log_potential_scraping(user_id, agent_id),
            
            # Notify security team
            await self._send_security_alert({
                "type": "potential_scraping",
                "user_id": user_id,
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        ]
```

---

### 10. **Compliance & Privacy Controls**

```python
class ComplianceManager:
    """Ensures compliance with data privacy regulations"""
    
    def apply_gdpr_compliance(self, user_id, agent_data_access):
        """Apply GDPR compliance measures"""
        
        compliance_measures = {
            "data_minimization": self._ensure_data_minimization(agent_data_access),
            "purpose_limitation": self._verify_purpose_limitation(agent_data_access),
            "consent_verification": self._verify_user_consent(user_id, "agent_data_access"),
            "right_to_be_forgotten": self._setup_deletion_mechanism(user_id),
            "data_portability": self._enable_data_export(user_id),
            "privacy_by_design": self._implement_privacy_controls()
        }
        
        return compliance_measures
    
    def generate_compliance_report(self, user_id, agent_id, timeframe="30d"):
        """Generate compliance audit report"""
        
        report = {
            "user_id": user_id,
            "agent_id": agent_id,
            "timeframe": timeframe,
            "data_accessed": self._get_data_access_summary(user_id, agent_id, timeframe),
            "consent_status": self._verify_consent_status(user_id),
            "retention_compliance": self._check_retention_policies(user_id),
            "security_incidents": self._get_security_incidents(user_id, agent_id, timeframe),
            "compliance_score": self._calculate_compliance_score(user_id, agent_id),
            "recommendations": self._generate_compliance_recommendations(user_id, agent_id)
        }
        
        return report
```

---

## 🔧 Implementation in OppGrid

### Backend Implementation

```python
# app/services/agent_security.py
from .agent_security_protocols import (
    AgentCapabilityToken, 
    DataAccessFilter, 
    AgentRateLimiter,
    SensitiveDataProtector,
    AgentAuditLogger
)

class AgentSecurityService:
    """Main security service for AI agents"""
    
    def __init__(self, db_session, redis_client, encryption_key):
        self.db = db_session
        self.redis = redis_client
        self.encryption_key = encryption_key
        
        # Initialize security components
        self.rate_limiter = AgentRateLimiter(redis_client)
        self.data_filter = DataAccessFilter()
        self.data_protector = SensitiveDataProtector(encryption_key)
        self.audit_logger = AgentAuditLogger(db_session, redis_client)
    
    async def process_agent_request(self, user_id, agent_id, action, requested_data):
        """Main security checkpoint for all agent requests"""
        
        # 1. Verify subscription and permissions
        user_tier = await self.get_user_subscription_tier(user_id)
        agent_token = await self.create_agent_capability_token(user_id, agent_id, action)
        
        # 2. Apply rate limiting
        rate_limit_ok, rate_limit_message = await self.rate_limiter.check_rate_limit(
            user_id, agent_id, action
        )
        if not rate_limit_ok:
            await self.audit_logger.log_agent_access(
                user_id, agent_id, action, requested_data, success=False
            )
            raise RateLimitExceeded(rate_limit_message)
        
        # 3. Filter data based on subscription tier
        filtered_data = await self._apply_tier_based_filtering(
            requested_data, user_tier, action
        )
        
        # 4. Protect sensitive fields
        protected_data = self.data_protector.protect_sensitive_fields(
            filtered_data, "medium"  # Based on data sensitivity
        )
        
        # 5. Create audit trail
        await self.audit_logger.log_agent_access(
            user_id, agent_id, action, protected_data, success=True
        )
        
        return protected_data
```

---

## 🎯 Summary

### Security Layers Implemented:

1. **🔐 Subscription-Based Access Control** - Agents can only access data appropriate to user's tier
2. **🚫 Field-Level Data Filtering** - Sensitive fields automatically removed/masked
3. **⏱️ Rate Limiting** - Prevents abuse and data scraping
4. **🔒 Data Encryption** - Sensitive data encrypted at rest and in transit
5. **📊 Comprehensive Audit Trail** - Every agent action logged and monitored
6. **🛡️ Agent Isolation** - Agents operate in sandboxed environments
7. **⚡ Dynamic Permissions** - Real-time permission updates with grace periods
8. **🚨 Breach Prevention** - Detects and prevents suspicious data access patterns
9. **📋 Compliance Controls** - GDPR, privacy-by-design implementation
10. **🔄 Token-Based Access** - Time-limited, scoped access tokens

### **Bottom Line**: 
- **Free users**: Can only see basic opportunity info, no AI analysis
- **Pro users**: Get full AI analysis but limited to 50 calls/day
- **Business users**: Can create custom agents, higher limits
- **Enterprise users**: Unlimited access with advanced security controls

**No agent can ever access data beyond their user's subscription level!** 🛡️

Ready to implement these security protocols? 🚀