from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.subscription import SubscriptionTier, UnlockedOpportunity
from app.models.user import User
from app.services.stripe_service import stripe_service
from app.services.usage_service import usage_service


@dataclass(frozen=True)
class OpportunityEntitlements:
    is_authenticated: bool
    user_tier: Optional[SubscriptionTier]
    age_days: int
    freshness_badge: dict
    is_unlocked: bool
    unlock_method: Optional[str]
    is_accessible_by_tier: bool
    is_accessible: bool
    days_until_unlock: int
    can_pay_to_unlock: bool
    unlock_price: Optional[int]
    deep_dive_available: bool
    execution_package_available: bool


def _utc_age_days(created_at: datetime | None) -> int:
    now = datetime.now(timezone.utc)
    if created_at is None:
        created_at = now
    elif created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return (now - created_at).days


def get_opportunity_entitlements(
    db: Session,
    opportunity: Opportunity,
    user: User | None,
) -> OpportunityEntitlements:
    """
    Single source of truth for opportunity access rules.

    Notes:
    - `is_accessible_by_tier` is purely time-decay tier access.
    - `is_accessible` includes any explicit unlock record.
    """

    is_authenticated = user is not None
    age_days = _utc_age_days(opportunity.created_at)
    freshness_badge = stripe_service.get_opportunity_freshness_badge(age_days)

    user_tier: SubscriptionTier | None = None
    is_unlocked = False
    unlock_method: str | None = None

    if user:
        subscription = usage_service.get_or_create_subscription(user, db)
        user_tier = subscription.tier if isinstance(subscription.tier, SubscriptionTier) else SubscriptionTier(subscription.tier)

        # NOTE: usage_service.is_opportunity_unlocked treats authors as unlocked.
        is_unlocked = usage_service.is_opportunity_unlocked(user, opportunity.id, db)
        if is_unlocked:
            unlock_record = db.query(UnlockedOpportunity).filter(
                UnlockedOpportunity.user_id == user.id,
                UnlockedOpportunity.opportunity_id == opportunity.id,
            ).first()
            if unlock_record and unlock_record.unlock_method:
                unlock_method = unlock_record.unlock_method.value

            # Expiration handling (pay-per-unlock)
            if unlock_record and unlock_record.expires_at:
                now = datetime.now(timezone.utc)
                exp = unlock_record.expires_at
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                if now > exp:
                    is_unlocked = False
                    unlock_method = None

    # If unauthenticated, treat as Free for countdown calculations, but not accessible
    effective_tier = user_tier or SubscriptionTier.FREE
    is_accessible_by_tier = is_authenticated and stripe_service.can_access_opportunity_by_age(effective_tier, age_days)
    days_until_unlock = stripe_service.get_days_until_unlock(effective_tier, age_days)

    # Pay-per-unlock availability policy (current): Free tier + Archive (91+ days) + not already unlocked
    can_pay_to_unlock = (age_days >= 91) and (not is_authenticated or effective_tier == SubscriptionTier.FREE) and (not is_unlocked)
    unlock_price = stripe_service.PAY_PER_UNLOCK_PRICE if can_pay_to_unlock else None

    is_accessible = is_accessible_by_tier or is_unlocked

    tier_value = effective_tier.value
    deep_dive_available = tier_value in ["business", "enterprise"] and is_accessible
    execution_package_available = tier_value in ["business", "enterprise"] and is_accessible

    return OpportunityEntitlements(
        is_authenticated=is_authenticated,
        user_tier=user_tier,
        age_days=age_days,
        freshness_badge=freshness_badge,
        is_unlocked=is_unlocked,
        unlock_method=unlock_method,
        is_accessible_by_tier=is_accessible_by_tier,
        is_accessible=is_accessible,
        days_until_unlock=days_until_unlock,
        can_pay_to_unlock=can_pay_to_unlock,
        unlock_price=unlock_price,
        deep_dive_available=deep_dive_available,
        execution_package_available=execution_package_available,
    )

