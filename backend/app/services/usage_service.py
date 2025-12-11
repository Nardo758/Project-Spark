"""
Usage Tracking Service

Manages user quotas and usage tracking for subscription tiers
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Tuple

from app.models.user import User
from app.models.subscription import Subscription, UsageRecord, UnlockedOpportunity, SubscriptionTier
from app.models.opportunity import Opportunity
from app.services.stripe_service import stripe_service


class UsageService:
    """Service for tracking and enforcing usage limits"""

    @staticmethod
    def get_or_create_subscription(user: User, db: Session) -> Subscription:
        """
        Get user's subscription or create free tier

        Args:
            user: User object
            db: Database session

        Returns:
            Subscription object
        """
        if not user.subscription:
            subscription = Subscription(
                user_id=user.id,
                tier=SubscriptionTier.FREE,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            return subscription

        return user.subscription

    @staticmethod
    def get_current_usage(user: User, db: Session) -> Optional[UsageRecord]:
        """
        Get current billing period's usage record

        Args:
            user: User object
            db: Database session

        Returns:
            UsageRecord or None
        """
        subscription = UsageService.get_or_create_subscription(user, db)

        # Check if we need to create new usage record for current period
        now = datetime.utcnow()

        # Find usage record for current period
        usage = db.query(UsageRecord).filter(
            UsageRecord.user_id == user.id,
            UsageRecord.period_start <= now,
            UsageRecord.period_end >= now
        ).first()

        if not usage:
            # Create new usage record for current period
            usage = UsageRecord(
                user_id=user.id,
                period_start=subscription.current_period_start or now,
                period_end=subscription.current_period_end or (now + timedelta(days=30))
            )
            db.add(usage)
            db.commit()
            db.refresh(usage)

        return usage

    @staticmethod
    def can_unlock_opportunity(user: User, db: Session) -> Tuple[bool, str]:
        """
        Check if user can unlock another opportunity

        Returns:
            (can_unlock, reason_if_not)
        """
        subscription = UsageService.get_or_create_subscription(user, db)
        usage = UsageService.get_current_usage(user, db)

        can_unlock = stripe_service.can_unlock_opportunity(
            subscription.tier,
            usage.unlocked_opportunities
        )

        if not can_unlock:
            limits = stripe_service.get_tier_limits(subscription.tier)
            return False, f"Monthly unlock limit reached ({limits['monthly_unlocks']} unlocks)"

        return True, ""

    @staticmethod
    def unlock_opportunity(user: User, opportunity_id: int, db: Session) -> Tuple[bool, str]:
        """
        Unlock an opportunity for viewing

        Returns:
            (success, message)
        """
        # Check if already unlocked
        existing = db.query(UnlockedOpportunity).filter(
            UnlockedOpportunity.user_id == user.id,
            UnlockedOpportunity.opportunity_id == opportunity_id
        ).first()

        if existing:
            return True, "Already unlocked"

        # Check if can unlock
        can_unlock, reason = UsageService.can_unlock_opportunity(user, db)
        if not can_unlock:
            return False, reason

        # Check if opportunity exists
        opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opportunity:
            return False, "Opportunity not found"

        # Create unlock record
        unlock = UnlockedOpportunity(
            user_id=user.id,
            opportunity_id=opportunity_id
        )
        db.add(unlock)

        # Update usage
        usage = UsageService.get_current_usage(user, db)
        usage.unlocked_opportunities += 1
        usage.opportunity_views += 1

        db.commit()

        return True, "Opportunity unlocked"

    @staticmethod
    def is_opportunity_unlocked(user: User, opportunity_id: int, db: Session) -> bool:
        """Check if user has unlocked an opportunity"""
        # Authors can always see their own opportunities
        opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if opportunity and opportunity.author_id == user.id:
            return True

        unlock = db.query(UnlockedOpportunity).filter(
            UnlockedOpportunity.user_id == user.id,
            UnlockedOpportunity.opportunity_id == opportunity_id
        ).first()

        return unlock is not None

    @staticmethod
    def can_export(user: User, batch_size: int, db: Session) -> Tuple[bool, str]:
        """
        Check if user can export opportunities

        Returns:
            (can_export, reason_if_not)
        """
        subscription = UsageService.get_or_create_subscription(user, db)
        usage = UsageService.get_current_usage(user, db)

        can_export = stripe_service.can_export(
            subscription.tier,
            usage.ideas_exported,
            batch_size
        )

        if not can_export:
            limits = stripe_service.get_tier_limits(subscription.tier)

            if limits["export_limit"] == 0:
                return False, f"Exports not available on {subscription.tier.value} tier"

            if limits["export_batch_size"] != -1 and batch_size > limits["export_batch_size"]:
                return False, f"Batch size exceeds limit ({limits['export_batch_size']} ideas max)"

            return False, f"Monthly export limit reached ({limits['export_limit']} ideas)"

        return True, ""

    @staticmethod
    def record_export(user: User, idea_count: int, db: Session) -> None:
        """Record an export action"""
        usage = UsageService.get_current_usage(user, db)
        usage.csv_exports += 1
        usage.ideas_exported += idea_count
        db.commit()

    @staticmethod
    def get_remaining_unlocks(user: User, db: Session) -> int:
        """Get remaining unlocks for current period"""
        subscription = UsageService.get_or_create_subscription(user, db)
        usage = UsageService.get_current_usage(user, db)

        limits = stripe_service.get_tier_limits(subscription.tier)
        monthly_limit = limits["monthly_unlocks"]

        if monthly_limit == -1:
            return -1  # Unlimited

        return max(0, monthly_limit - usage.unlocked_opportunities)

    @staticmethod
    def reset_usage_if_needed(user: User, db: Session) -> None:
        """Reset usage if billing period has ended"""
        subscription = UsageService.get_or_create_subscription(user, db)
        now = datetime.utcnow()

        # Check if current period has ended
        if subscription.current_period_end and now > subscription.current_period_end:
            # Update period dates
            subscription.current_period_start = now
            subscription.current_period_end = now + timedelta(days=30)

            # New usage record will be created automatically on next access
            db.commit()


usage_service = UsageService()
