"""
Stripe Payment Service

Handles Stripe integration for subscriptions and payments
Uses Replit Stripe connector integration when available
"""

import stripe
import os
import logging
import requests
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from app.models.subscription import SubscriptionTier

logger = logging.getLogger(__name__)


def get_stripe_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Get Stripe API keys from Replit connector or environment.
    
    Returns:
        Tuple of (secret_key, publishable_key)
    """
    hostname = os.getenv("REPLIT_CONNECTORS_HOSTNAME")
    repl_identity = os.getenv("REPL_IDENTITY")
    web_repl_renewal = os.getenv("WEB_REPL_RENEWAL")
    
    if hostname and (repl_identity or web_repl_renewal):
        try:
            x_replit_token = f"repl {repl_identity}" if repl_identity else f"depl {web_repl_renewal}"
            is_production = os.getenv("REPLIT_DEPLOYMENT") == "1"
            target_env = "production" if is_production else "development"
            
            response = requests.get(
                f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=stripe&environment={target_env}",
                headers={
                    "Accept": "application/json",
                    "X_REPLIT_TOKEN": x_replit_token
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            if items:
                settings_data = items[0].get("settings", {})
                secret_key = settings_data.get("secret")
                publishable_key = settings_data.get("publishable")
                if secret_key:
                    logger.info("Using Stripe credentials from Replit connector")
                    return secret_key, publishable_key
        except Exception as e:
            logger.warning(f"Failed to get Stripe credentials from connector: {e}")
    
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
    if secret_key:
        logger.info("Using Stripe credentials from environment variables")
    return secret_key, publishable_key


def get_stripe_client():
    """
    Get a configured Stripe client with fresh credentials.
    Call this before each Stripe API operation to ensure valid credentials.
    
    Returns:
        The stripe module with api_key set
    
    Raises:
        ValueError: If Stripe credentials are not configured
    """
    secret_key, _ = get_stripe_credentials()
    if not secret_key:
        raise ValueError(
            "Stripe API key not configured. "
            "Set up the Stripe connector in Replit or set STRIPE_SECRET_KEY environment variable."
        )
    stripe.api_key = secret_key
    return stripe


def init_stripe():
    """Initialize Stripe with credentials from connector or environment"""
    try:
        secret_key, _ = get_stripe_credentials()
        if secret_key:
            stripe.api_key = secret_key
            logger.info("Stripe initialized successfully")
        else:
            logger.warning("Stripe API key not configured - payment features will not work until configured")
    except Exception as e:
        logger.warning(f"Failed to initialize Stripe: {e} - payment features will not work until configured")


# Try to initialize on module load, but don't fail if not configured
init_stripe()


class StripeService:
    """Service for Stripe payment operations"""

    # Time-decay access windows (days)
    TIER_ACCESS_WINDOWS = {
        SubscriptionTier.FREE: 91,       # Archive: 91+ days old
        SubscriptionTier.PRO: 31,        # Validated: 31+ days old  
        SubscriptionTier.BUSINESS: 8,    # Fresh: 8+ days old
        SubscriptionTier.ENTERPRISE: 0,  # Real-time: all opportunities
    }

    # Pay-per-unlock pricing
    PAY_PER_UNLOCK_PRICE = 1500  # $15.00 in cents
    FAST_PASS_PRICE = 9900  # $99.00 in cents (Business HOT fast-pass)

    # Subscription tier limits (updated per pricing strategy)
    TIER_LIMITS = {
        SubscriptionTier.FREE: {
            "monthly_views": 10,
            "monthly_unlocks": 0,  # Must pay per unlock
            "export_limit": 0,
            "export_batch_size": 0,
            "api_access": False,
            "price": 0,
            "access_window_days": 91,
            "daily_unlock_limit": 5,  # Max pay-per-unlocks per day
        },
        SubscriptionTier.PRO: {
            "monthly_views": -1,  # Unlimited for 31+ day opportunities
            "monthly_unlocks": -1,  # Unlimited for 31+ day opportunities
            "export_limit": 100,
            "export_batch_size": 1,
            "api_access": False,
            "price": 99,
            "access_window_days": 31,
        },
        SubscriptionTier.BUSINESS: {
            "monthly_views": -1,  # Unlimited for 8+ day opportunities
            "monthly_unlocks": -1,  # Unlimited
            "export_limit": 500,
            "export_batch_size": 50,
            "api_access": True,
            "price": 499,
            "access_window_days": 8,
            "execution_packages_monthly": 5,
        },
        SubscriptionTier.ENTERPRISE: {
            "monthly_views": -1,  # Unlimited
            "monthly_unlocks": -1,  # Unlimited
            "export_limit": -1,  # Unlimited
            "export_batch_size": -1,  # Unlimited
            "api_access": True,
            "price": 2500,  # Starting price
            "access_window_days": 0,
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
        client = get_stripe_client()
        customer = client.Customer.create(
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
        client = get_stripe_client()
        session = client.checkout.Session.create(
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
        client = get_stripe_client()
        session = client.billing_portal.Session.create(
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
        client = get_stripe_client()
        if at_period_end:
            subscription = client.subscriptions.update(
                subscription_id,
                cancel_at_period_end=True
            )
        else:
            subscription = client.subscriptions.cancel(subscription_id)
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
        client = get_stripe_client()
        subscription = client.Subscription.modify(
            subscription_id,
            cancel_at_period_end=False
        )
        return subscription

    @staticmethod
    def get_subscription(subscription_id: str) -> stripe.Subscription:
        """Get subscription details from Stripe"""
        client = get_stripe_client()
        return client.Subscription.retrieve(subscription_id)

    @staticmethod
    def get_customer(customer_id: str) -> stripe.Customer:
        """Get customer details from Stripe"""
        client = get_stripe_client()
        return client.Customer.retrieve(customer_id)

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
        client = get_stripe_client()
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        if not webhook_secret:
            raise ValueError("STRIPE_WEBHOOK_SECRET not configured")
        return client.Webhook.construct_event(payload, sig_header, webhook_secret)

    @staticmethod
    def get_tier_limits(tier: SubscriptionTier) -> Dict[str, Any]:
        """Get usage limits for a subscription tier"""
        return StripeService.TIER_LIMITS.get(tier, StripeService.TIER_LIMITS[SubscriptionTier.FREE])

    @staticmethod
    def get_access_window_days(tier: SubscriptionTier) -> int:
        """Get minimum opportunity age (in days) accessible for a tier"""
        return StripeService.TIER_ACCESS_WINDOWS.get(tier, 91)

    @staticmethod
    def can_access_opportunity_by_age(tier: SubscriptionTier, opportunity_age_days: int) -> bool:
        """
        Check if a tier can access an opportunity based on its age.
        
        Time-decay model:
        - Enterprise: 0+ days (real-time)
        - Business: 8+ days (fresh)
        - Pro: 31+ days (validated)
        - Free: 91+ days (archive, requires pay-per-unlock)
        """
        min_age = StripeService.get_access_window_days(tier)
        return opportunity_age_days >= min_age

    @staticmethod
    def get_opportunity_freshness_badge(age_days: int) -> Dict[str, str]:
        """
        Get freshness badge based on opportunity age.
        
        Returns dict with badge info (icon, label, color, tier_required)
        """
        if age_days <= 7:
            return {
                "icon": "🔥",
                "label": "HOT",
                "color": "#ef4444",  # red-500
                "tier_required": "enterprise",
                "description": "Exclusive intelligence window"
            }
        elif age_days <= 30:
            return {
                "icon": "⚡",
                "label": "FRESH",
                "color": "#f97316",  # orange-500
                "tier_required": "business",
                "description": "Early mover advantage"
            }
        elif age_days <= 90:
            return {
                "icon": "✓",
                "label": "VALIDATED",
                "color": "#22c55e",  # green-500
                "tier_required": "pro",
                "description": "Market-validated opportunity"
            }
        else:
            return {
                "icon": "📚",
                "label": "ARCHIVE",
                "color": "#6b7280",  # gray-500
                "tier_required": "free",
                "description": "Historical intelligence"
            }

    @staticmethod
    def get_days_until_unlock(tier: SubscriptionTier, opportunity_age_days: int) -> int:
        """
        Get number of days until an opportunity unlocks for a tier.
        Returns 0 if already accessible, negative if past unlock date.
        """
        min_age = StripeService.get_access_window_days(tier)
        return max(0, min_age - opportunity_age_days)

    @staticmethod
    def create_payment_intent_for_unlock(
        customer_id: str,
        opportunity_id: int,
        user_id: int
    ):
        """
        Create a Stripe PaymentIntent for one-time unlock.
        Default is pay-per-unlock ($15). Callers may override amount/type.
        """
        client = get_stripe_client()
        return client.PaymentIntent.create(
            amount=StripeService.PAY_PER_UNLOCK_PRICE,
            currency="usd",
            customer=customer_id,
            metadata={
                "type": "pay_per_unlock",
                "opportunity_id": str(opportunity_id),
                "user_id": str(user_id)
            },
            automatic_payment_methods={"enabled": True}
        )

    @staticmethod
    def create_payment_intent_for_one_time_unlock(
        customer_id: str,
        opportunity_id: int,
        user_id: int,
        *,
        amount_cents: int,
        unlock_type: str,
    ):
        """
        Create a PaymentIntent for one-time access grants (pay-per-unlock / fast-pass).
        """
        client = get_stripe_client()
        return client.PaymentIntent.create(
            amount=int(amount_cents),
            currency="usd",
            customer=customer_id,
            metadata={
                "type": unlock_type,
                "opportunity_id": str(opportunity_id),
                "user_id": str(user_id),
            },
            automatic_payment_methods={"enabled": True},
        )

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
