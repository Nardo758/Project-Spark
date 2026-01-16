"""
Slot Service - Manages opportunity slot balances and purchases
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.subscription import UserSlotBalance, OpportunityClaimLimit, UnlockedOpportunity, UnlockMethod, SubscriptionTier
from app.models.opportunity import Opportunity
from app.services.stripe_service import StripeService, get_stripe_client

MIN_CLAIM_LIMIT = 3
MAX_CLAIM_LIMIT = 10

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
    
    @staticmethod
    def get_or_create_claim_limit(opportunity_id: int, db: Session) -> OpportunityClaimLimit:
        """Get or create claim limit record for an opportunity"""
        claim_limit = db.query(OpportunityClaimLimit).filter(
            OpportunityClaimLimit.opportunity_id == opportunity_id
        ).first()
        
        if not claim_limit:
            claim_limit = OpportunityClaimLimit(
                opportunity_id=opportunity_id,
                claim_limit=MAX_CLAIM_LIMIT,
                claimed_count=0
            )
            db.add(claim_limit)
            db.commit()
            db.refresh(claim_limit)
        
        return claim_limit
    
    @staticmethod
    def claim_opportunity(user: User, opportunity_id: int, db: Session) -> Tuple[bool, str]:
        """
        Claim an opportunity using a slot.
        Uses row-level locking to prevent race conditions.
        
        Returns (success, message)
        """
        from sqlalchemy.exc import IntegrityError
        
        try:
            opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
            if not opportunity:
                return False, "Opportunity not found"
            
            existing = db.query(UnlockedOpportunity).filter(
                UnlockedOpportunity.user_id == user.id,
                UnlockedOpportunity.opportunity_id == opportunity_id
            ).first()
            if existing:
                return False, "You have already claimed this opportunity"
            
            claim_limit = db.query(OpportunityClaimLimit).filter(
                OpportunityClaimLimit.opportunity_id == opportunity_id
            ).with_for_update().first()
            
            if not claim_limit:
                try:
                    claim_limit = OpportunityClaimLimit(
                        opportunity_id=opportunity_id,
                        claim_limit=MAX_CLAIM_LIMIT,
                        claimed_count=0
                    )
                    db.add(claim_limit)
                    db.flush()
                except IntegrityError:
                    db.rollback()
                    claim_limit = db.query(OpportunityClaimLimit).filter(
                        OpportunityClaimLimit.opportunity_id == opportunity_id
                    ).with_for_update().first()
            
            if claim_limit.claimed_count >= claim_limit.claim_limit:
                db.rollback()
                return False, f"This opportunity has reached its exclusivity limit ({claim_limit.claim_limit} users)"
            
            balance = db.query(UserSlotBalance).filter(
                UserSlotBalance.user_id == user.id
            ).with_for_update().first()
            
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
                db.flush()
            
            available = (balance.monthly_slots + balance.bonus_slots) - balance.used_slots
            if available <= 0:
                db.rollback()
                return False, "No slots available. Purchase additional slots to continue."
            
            balance.used_slots += 1
            claim_limit.claimed_count += 1
            
            unlocked = UnlockedOpportunity(
                user_id=user.id,
                opportunity_id=opportunity_id,
                unlock_method=UnlockMethod.SLOT_CLAIM,
                amount_paid=0
            )
            db.add(unlocked)
            
            db.commit()
            
            remaining = (balance.monthly_slots + balance.bonus_slots) - balance.used_slots
            slots_remaining = claim_limit.claim_limit - claim_limit.claimed_count
            
            logger.info(f"User {user.id} claimed opportunity {opportunity_id}. User slots remaining: {remaining}, Opportunity slots: {slots_remaining}")
            
            return True, f"Opportunity claimed successfully. {slots_remaining} exclusive slots remaining for this opportunity."
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error claiming opportunity {opportunity_id} for user {user.id}: {e}")
            return False, "An error occurred while claiming the opportunity. Please try again."
    
    @staticmethod
    def get_opportunity_claim_status(opportunity_id: int, db: Session) -> dict:
        """Get claim status for an opportunity"""
        claim_limit = SlotService.get_or_create_claim_limit(opportunity_id, db)
        
        return {
            "opportunity_id": opportunity_id,
            "claim_limit": claim_limit.claim_limit,
            "claimed_count": claim_limit.claimed_count,
            "slots_remaining": claim_limit.slots_remaining,
            "is_available": claim_limit.is_available,
        }
    
    @staticmethod
    def set_claim_limit(opportunity_id: int, limit: int, db: Session) -> OpportunityClaimLimit:
        """Set the claim limit for an opportunity (admin only)"""
        if limit < MIN_CLAIM_LIMIT or limit > MAX_CLAIM_LIMIT:
            raise ValueError(f"Claim limit must be between {MIN_CLAIM_LIMIT} and {MAX_CLAIM_LIMIT}")
        
        claim_limit = SlotService.get_or_create_claim_limit(opportunity_id, db)
        claim_limit.claim_limit = limit
        db.commit()
        db.refresh(claim_limit)
        
        logger.info(f"Set claim limit for opportunity {opportunity_id} to {limit}")
        return claim_limit


slot_service = SlotService()
