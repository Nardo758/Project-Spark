"""
Slot Service - Manages opportunity slot balances and purchases
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.subscription import UserSlotBalance, SubscriptionTier
from app.services.stripe_service import StripeService, get_stripe_client

logger = logging.getLogger(__name__)

SLOT_PRICE_IDS = {
    SubscriptionTier.STARTER: os.getenv("STRIPE_SLOT_PRICE_STARTER"),
    SubscriptionTier.GROWTH: os.getenv("STRIPE_SLOT_PRICE_GROWTH"),
    SubscriptionTier.PRO: os.getenv("STRIPE_SLOT_PRICE_PRO"),
    SubscriptionTier.TEAM: os.getenv("STRIPE_SLOT_PRICE_TEAM"),
    SubscriptionTier.BUSINESS: os.getenv("STRIPE_SLOT_PRICE_BUSINESS"),
    SubscriptionTier.ENTERPRISE: os.getenv("STRIPE_SLOT_PRICE_ENTERPRISE"),
}


class SlotService:
    """Service for managing opportunity slot balances"""
    
    @staticmethod
    def get_or_create_balance(user: User, db: Session) -> UserSlotBalance:
        """Get or create a slot balance record for a user"""
        balance = db.query(UserSlotBalance).filter(
            UserSlotBalance.user_id == user.id
        ).first()
        
        if not balance:
            tier = user.subscription.tier if user.subscription else SubscriptionTier.FREE
            monthly_slots = StripeService.get_monthly_slots(tier)
            
            balance = UserSlotBalance(
                user_id=user.id,
                monthly_slots=monthly_slots,
                bonus_slots=0,
                used_slots=0,
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow() + timedelta(days=30)
            )
            db.add(balance)
            db.commit()
            db.refresh(balance)
        
        return balance
    
    @staticmethod
    def get_available_slots(user: User, db: Session) -> int:
        """Get number of available slots for a user"""
        balance = SlotService.get_or_create_balance(user, db)
        SlotService._check_period_reset(balance, user, db)
        return (balance.monthly_slots + balance.bonus_slots) - balance.used_slots
    
    @staticmethod
    def _check_period_reset(balance: UserSlotBalance, user: User, db: Session) -> None:
        """Check if the billing period has ended and reset slots if needed"""
        if balance.period_end and datetime.utcnow() > balance.period_end:
            tier = user.subscription.tier if user.subscription else SubscriptionTier.FREE
            monthly_slots = StripeService.get_monthly_slots(tier)
            
            balance.monthly_slots = monthly_slots
            balance.bonus_slots = 0
            balance.used_slots = 0
            balance.period_start = datetime.utcnow()
            balance.period_end = datetime.utcnow() + timedelta(days=30)
            db.commit()
            logger.info(f"Reset slot balance for user {user.id}: {monthly_slots} slots")
    
    @staticmethod
    def use_slot(user: User, db: Session) -> Tuple[bool, str]:
        """
        Use one slot from the user's balance.
        Returns (success, message)
        """
        balance = SlotService.get_or_create_balance(user, db)
        SlotService._check_period_reset(balance, user, db)
        
        available = (balance.monthly_slots + balance.bonus_slots) - balance.used_slots
        
        if available <= 0:
            return False, "No slots available. Purchase additional slots to continue."
        
        balance.used_slots += 1
        db.commit()
        
        remaining = (balance.monthly_slots + balance.bonus_slots) - balance.used_slots
        logger.info(f"User {user.id} used a slot. Remaining: {remaining}")
        
        return True, f"Slot used. {remaining} slots remaining this period."
    
    @staticmethod
    def add_bonus_slots(user: User, quantity: int, db: Session) -> UserSlotBalance:
        """Add bonus slots from a purchase"""
        balance = SlotService.get_or_create_balance(user, db)
        balance.bonus_slots += quantity
        db.commit()
        db.refresh(balance)
        logger.info(f"Added {quantity} bonus slots to user {user.id}")
        return balance
    
    @staticmethod
    def create_slot_checkout_session(
        user: User,
        quantity: int,
        success_url: str,
        cancel_url: str,
        db: Session
    ) -> dict:
        """Create a Stripe checkout session for purchasing extra slots"""
        tier = user.subscription.tier if user.subscription else SubscriptionTier.STARTER
        price_id = SLOT_PRICE_IDS.get(tier)
        
        if not price_id:
            raise ValueError(f"No slot price configured for tier {tier}")
        
        customer_id = None
        if user.subscription and user.subscription.stripe_customer_id:
            customer_id = user.subscription.stripe_customer_id
        
        client = get_stripe_client()
        
        session_params = {
            "mode": "payment",
            "line_items": [{
                "price": price_id,
                "quantity": quantity,
            }],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "user_id": str(user.id),
                "type": "slot_purchase",
                "quantity": str(quantity),
                "tier": tier.value,
            }
        }
        
        if customer_id:
            session_params["customer"] = customer_id
        else:
            session_params["customer_email"] = user.email
        
        session = client.checkout.Session.create(**session_params)
        
        return {
            "session_id": session.id,
            "url": session.url
        }
    
    @staticmethod
    def get_slot_price(tier: SubscriptionTier) -> int:
        """Get the slot price in cents for a tier"""
        return StripeService.get_extra_slot_price(tier)
    
    @staticmethod
    def get_balance_info(user: User, db: Session) -> dict:
        """Get detailed balance information for a user"""
        balance = SlotService.get_or_create_balance(user, db)
        SlotService._check_period_reset(balance, user, db)
        
        tier = user.subscription.tier if user.subscription else SubscriptionTier.FREE
        slot_price_cents = SlotService.get_slot_price(tier)
        
        return {
            "monthly_slots": balance.monthly_slots,
            "bonus_slots": balance.bonus_slots,
            "used_slots": balance.used_slots,
            "available_slots": (balance.monthly_slots + balance.bonus_slots) - balance.used_slots,
            "period_start": balance.period_start.isoformat() if balance.period_start else None,
            "period_end": balance.period_end.isoformat() if balance.period_end else None,
            "extra_slot_price_cents": slot_price_cents,
            "extra_slot_price": f"${slot_price_cents / 100:.2f}",
        }


slot_service = SlotService()
