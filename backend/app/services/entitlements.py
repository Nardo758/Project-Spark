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
    unlock_expires_at: Optional[datetime]
    content_state: str  # full | preview | placeholder | locked | pay_per_unlock | fast_pass
    deep_dive_available: bool
    can_buy_deep_dive: bool  # Pro tier can buy Layer 2 for $49
    deep_dive_price: Optional[int]  # Price in cents (4900 = $49)
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
    unlock_expires_at: datetime | None = None

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
                    unlock_expires_at = None
                else:
                    unlock_expires_at = exp

    # If unauthenticated, treat as Free for countdown calculations, but not accessible
    effective_tier = user_tier or SubscriptionTier.FREE
    is_accessible_by_tier = is_authenticated and stripe_service.can_access_opportunity_by_age(effective_tier, age_days)
    days_until_unlock = stripe_service.get_days_until_unlock(effective_tier, age_days)

    # One-time unlock policies:
    # - Free tier: Archive (91+ days) can pay-per-unlock $15 (Layer 1) if not already unlocked.
    # - Business tier: HOT (0-7 days) can optionally "fast pass" a single opportunity for $99 if not already unlocked.
    can_pay_to_unlock = False
    unlock_price: int | None = None

    if not is_unlocked:
        if effective_tier == SubscriptionTier.FREE and age_days >= 91:
            can_pay_to_unlock = True
            unlock_price = stripe_service.PAY_PER_UNLOCK_PRICE
        elif is_authenticated and effective_tier == SubscriptionTier.BUSINESS and age_days <= 7:
            can_pay_to_unlock = True
            unlock_price = stripe_service.FAST_PASS_PRICE

    is_accessible = is_accessible_by_tier or is_unlocked

    tier_value = effective_tier.value
    
    # Deep Dive (Layer 2) access logic:
    # - Business/Enterprise: included with tier access
    # - Pro: available for $49 add-on (check has_deep_dive field)
    # - Free: not available
    has_paid_deep_dive = False
    if user:
        unlock_record = db.query(UnlockedOpportunity).filter(
            UnlockedOpportunity.user_id == user.id,
            UnlockedOpportunity.opportunity_id == opportunity.id,
        ).first()
        if unlock_record and unlock_record.has_deep_dive:
            has_paid_deep_dive = True
    
    deep_dive_available = (
        (tier_value in ["business", "enterprise"] and is_accessible) or
        has_paid_deep_dive
    )
    
    # Pro tier can buy Deep Dive ($49) if they have base access but not Deep Dive yet
    can_buy_deep_dive = (
        is_authenticated and
        tier_value == "pro" and
        is_accessible and
        not has_paid_deep_dive
    )
    deep_dive_price = stripe_service.DEEP_DIVE_PRICE if can_buy_deep_dive else None
    
    execution_package_available = tier_value in ["business", "enterprise"] and is_accessible

    # UI/content state guidance (single source of truth):
    # This drives "preview vs placeholder vs full" behaviors.
    if is_accessible:
        content_state = "full"
    else:
        if not is_authenticated:
            content_state = "locked"
        elif effective_tier == SubscriptionTier.FREE:
            content_state = "pay_per_unlock" if age_days >= 91 else "locked"
        elif effective_tier == SubscriptionTier.PRO:
            # Pro: 31+ full Layer 1; 8-30 preview; 0-7 placeholder
            if age_days <= 7:
                content_state = "placeholder"
            elif age_days <= 30:
                content_state = "preview"
            else:
                content_state = "locked"
        elif effective_tier == SubscriptionTier.BUSINESS:
            # Business: 8+ full Layer 1+2; 0-7 preview + fast-pass / enterprise
            content_state = "fast_pass" if age_days <= 7 else "locked"
        else:
            content_state = "locked"

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
        unlock_expires_at=unlock_expires_at,
        content_state=content_state,
        deep_dive_available=deep_dive_available,
        can_buy_deep_dive=can_buy_deep_dive,
        deep_dive_price=deep_dive_price,
        execution_package_available=execution_package_available,
    )

