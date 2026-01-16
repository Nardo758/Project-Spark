#!/usr/bin/env python3
"""
Initialize slot balances for existing users based on their subscription tier.
Run this after migrating to the new 6-tier pricing model.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.db.database import SessionLocal
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier, UserSlotBalance
from app.services.stripe_service import StripeService

TIER_MIGRATION_MAP = {
    "explorer": SubscriptionTier.STARTER,
    "builder": SubscriptionTier.GROWTH,
    "scaler": SubscriptionTier.PRO,
}

def init_slot_balances():
    """Initialize slot balances for all users with active subscriptions."""
    db = SessionLocal()
    
    try:
        users_with_subs = db.query(User).join(Subscription).filter(
            Subscription.tier != SubscriptionTier.FREE
        ).all()
        
        print(f"Found {len(users_with_subs)} users with active subscriptions")
        
        created = 0
        skipped = 0
        
        for user in users_with_subs:
            existing = db.query(UserSlotBalance).filter(
                UserSlotBalance.user_id == user.id
            ).first()
            
            if existing:
                print(f"  Skipping user {user.id} ({user.email}) - balance exists")
                skipped += 1
                continue
            
            tier = user.subscription.tier
            monthly_slots = StripeService.get_monthly_slots(tier)
            
            period_start = user.subscription.current_period_start or datetime.utcnow()
            period_end = user.subscription.current_period_end or (datetime.utcnow() + timedelta(days=30))
            
            balance = UserSlotBalance(
                user_id=user.id,
                monthly_slots=monthly_slots,
                purchased_slots=0,
                slots_used=0,
                period_start=period_start,
                period_end=period_end
            )
            db.add(balance)
            created += 1
            print(f"  Created balance for user {user.id} ({user.email}): {monthly_slots} monthly slots ({tier.value})")
        
        db.commit()
        print(f"\nDone! Created {created} slot balances, skipped {skipped} existing")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing slot balances for existing users...")
    init_slot_balances()
