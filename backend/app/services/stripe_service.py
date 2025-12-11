"""
Stripe Payment Service

Handles Stripe integration for subscriptions and payments
"""

import stripe
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.subscription import SubscriptionTier


# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class StripeService:
    """Service for Stripe payment operations"""

    # Subscription tier limits
    TIER_LIMITS = {
        SubscriptionTier.FREE: {
            "monthly_views": 10,
            "monthly_unlocks": 10,
            "export_limit": 0,
            "export_batch_size": 0,
            "api_access": False,
            "price": 0
        },
        SubscriptionTier.PRO: {
            "monthly_views": 100,
            "monthly_unlocks": 100,
            "export_limit": 100,
            "export_batch_size": 1,  # Single idea CSV only
            "api_access": False,
            "price": 49
        },
        SubscriptionTier.BUSINESS: {
            "monthly_views": 500,
            "monthly_unlocks": 500,
            "export_limit": 500,
            "export_batch_size": 50,
            "api_access": True,
            "price": 199
        },
        SubscriptionTier.ENTERPRISE: {
            "monthly_views": -1,  # Unlimited
            "monthly_unlocks": -1,  # Unlimited
            "export_limit": -1,  # Unlimited
            "export_batch_size": -1,  # Unlimited
            "api_access": True,
            "price": 0  # Custom pricing
        }
    }

    # Stripe Price IDs (set these in environment variables)
    STRIPE_PRICES = {
        SubscriptionTier.PRO: os.getenv("STRIPE_PRICE_PRO"),
        SubscriptionTier.BUSINESS: os.getenv("STRIPE_PRICE_BUSINESS"),
        # Enterprise is custom, handled separately
    }

    @staticmethod
    def create_customer(email: str, name: str, metadata: Optional[Dict] = None) -> stripe.Customer:
        """
        Create a Stripe customer

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata

        Returns:
            Stripe Customer object
        """
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {}
        )
        return customer

    @staticmethod
    def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict] = None
    ) -> stripe.checkout.Session:
        """
        Create a Stripe Checkout session for subscription

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if canceled
            metadata: Additional metadata

        Returns:
            Stripe Checkout Session
        """
        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {},
            allow_promotion_codes=True,
        )
        return session

    @staticmethod
    def create_portal_session(customer_id: str, return_url: str) -> stripe.billing_portal.Session:
        """
        Create a Stripe Customer Portal session

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session

        Returns:
            Stripe Portal Session
        """
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session

    @staticmethod
    def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> stripe.Subscription:
        """
        Cancel a Stripe subscription

        Args:
            subscription_id: Stripe subscription ID
            at_period_end: Whether to cancel at period end or immediately

        Returns:
            Updated Stripe Subscription
        """
        if at_period_end:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        else:
            subscription = stripe.Subscription.delete(subscription_id)
        return subscription

    @staticmethod
    def reactivate_subscription(subscription_id: str) -> stripe.Subscription:
        """
        Reactivate a canceled subscription

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Updated Stripe Subscription
        """
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=False
        )
        return subscription

    @staticmethod
    def get_subscription(subscription_id: str) -> stripe.Subscription:
        """Get subscription details from Stripe"""
        return stripe.Subscription.retrieve(subscription_id)

    @staticmethod
    def get_customer(customer_id: str) -> stripe.Customer:
        """Get customer details from Stripe"""
        return stripe.Customer.retrieve(customer_id)

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
        """
        Construct and verify a webhook event from Stripe

        Args:
            payload: Raw request body
            sig_header: Stripe signature header

        Returns:
            Verified Stripe Event

        Raises:
            ValueError: If signature verification fails
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

    @staticmethod
    def get_tier_limits(tier: SubscriptionTier) -> Dict[str, Any]:
        """Get usage limits for a subscription tier"""
        return StripeService.TIER_LIMITS.get(tier, StripeService.TIER_LIMITS[SubscriptionTier.FREE])

    @staticmethod
    def can_unlock_opportunity(tier: SubscriptionTier, current_unlocks: int) -> bool:
        """
        Check if user can unlock another opportunity

        Args:
            tier: User's subscription tier
            current_unlocks: Number of opportunities unlocked this period

        Returns:
            bool: True if user can unlock more
        """
        limits = StripeService.get_tier_limits(tier)
        monthly_limit = limits["monthly_unlocks"]

        # -1 means unlimited
        if monthly_limit == -1:
            return True

        return current_unlocks < monthly_limit

    @staticmethod
    def can_export(tier: SubscriptionTier, current_exports: int, batch_size: int) -> bool:
        """
        Check if user can export opportunities

        Args:
            tier: User's subscription tier
            current_exports: Number of ideas exported this period
            batch_size: Number of ideas in this export

        Returns:
            bool: True if user can export
        """
        limits = StripeService.get_tier_limits(tier)
        export_limit = limits["export_limit"]
        max_batch_size = limits["export_batch_size"]

        # Check if tier allows exports
        if export_limit == 0:
            return False

        # Check batch size
        if max_batch_size != -1 and batch_size > max_batch_size:
            return False

        # Check total limit
        if export_limit == -1:
            return True

        return current_exports + batch_size <= export_limit


stripe_service = StripeService()
