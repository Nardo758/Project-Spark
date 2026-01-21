from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if current_user.is_banned:
        raise HTTPException(status_code=403, detail="User is banned")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get the current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> User | None:
    """Get the current user if authenticated, otherwise return None"""
    if not token:
        return None
    
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    email: str = payload.get("sub")
    if email is None:
        return None
    
    user = db.query(User).filter(User.email == email).first()
    return user


from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from typing import List, Callable
from functools import wraps


def get_user_subscription_tier(user: User, db: Session) -> SubscriptionTier:
    """Get user's current subscription tier"""
    from datetime import datetime, timezone
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    if subscription:
        if subscription.current_period_end and subscription.current_period_end < datetime.now(timezone.utc):
            return SubscriptionTier.FREE
        return subscription.tier
    return SubscriptionTier.FREE


class RequireSubscription:
    """Dependency that requires a minimum subscription tier"""
    
    def __init__(self, min_tier: SubscriptionTier):
        self.min_tier = min_tier
        self.tier_hierarchy = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.STARTER: 1,
            SubscriptionTier.GROWTH: 2,
            SubscriptionTier.PRO: 3,
            SubscriptionTier.TEAM: 4,
            SubscriptionTier.BUSINESS: 5,
            SubscriptionTier.ENTERPRISE: 6
        }
    
    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        user_tier = get_user_subscription_tier(current_user, db)
        user_level = self.tier_hierarchy.get(user_tier, 0)
        required_level = self.tier_hierarchy.get(self.min_tier, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires a {self.min_tier.value} subscription or higher"
            )
        return current_user


async def require_any_paid_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """Require any active paid subscription (Starter or above)"""
    user_tier = get_user_subscription_tier(current_user, db)
    
    if user_tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An active subscription is required to access this feature. Please subscribe at /pricing."
        )
    return current_user


require_starter = RequireSubscription(SubscriptionTier.STARTER)
require_growth = RequireSubscription(SubscriptionTier.GROWTH)
require_pro = RequireSubscription(SubscriptionTier.PRO)
require_team = RequireSubscription(SubscriptionTier.TEAM)
require_business = RequireSubscription(SubscriptionTier.BUSINESS)
require_enterprise = RequireSubscription(SubscriptionTier.ENTERPRISE)
