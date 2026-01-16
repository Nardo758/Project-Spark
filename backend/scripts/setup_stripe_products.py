#!/usr/bin/env python3
"""
Script to create Stripe products and prices for the 6-tier subscription model.

Run this script once to set up all subscription products in Stripe.
After running, copy the price IDs to your environment variables.

Usage:
    python backend/scripts/setup_stripe_products.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.stripe_service import get_stripe_client

SUBSCRIPTION_TIERS = [
    {
        "name": "OppGrid Starter",
        "tier_key": "STARTER",
        "description": "Start exploring opportunities - 1 slot/month",
        "price_cents": 2000,
        "features": [
            "1 opportunity slot per month",
            "Full platform access",
            "AI execution reports (full price)",
            "Additional slots: $50 each"
        ]
    },
    {
        "name": "OppGrid Growth",
        "tier_key": "GROWTH", 
        "description": "Explore more opportunities - 3 slots/month, 10% report discount",
        "price_cents": 5000,
        "features": [
            "3 opportunity slots per month",
            "10% off all reports",
            "Priority support",
            "Additional slots: $40 each"
        ]
    },
    {
        "name": "OppGrid Pro",
        "tier_key": "PRO",
        "description": "Maximum individual power - 5 slots/month, 15% report discount",
        "price_cents": 9900,
        "features": [
            "5 opportunity slots per month",
            "15% off all reports",
            "Priority support",
            "Additional slots: $35 each"
        ]
    },
    {
        "name": "OppGrid Team",
        "tier_key": "TEAM",
        "description": "For small teams and consultants - 5 slots/month, 3 seats, white-label",
        "price_cents": 25000,
        "features": [
            "5 opportunity slots per month",
            "3 team seats",
            "White-label reports",
            "Full commercial use rights",
            "Additional slots: $30 each"
        ]
    },
    {
        "name": "OppGrid Business",
        "tier_key": "BUSINESS",
        "description": "Scale your consulting practice - 15 slots/month, 10 seats, 20% discount",
        "price_cents": 75000,
        "features": [
            "15 opportunity slots per month",
            "10 team seats",
            "White-label + 20% off reports",
            "API access",
            "Additional slots: $25 each"
        ]
    }
]

SLOT_ADDON_PRICES = [
    {"tier": "STARTER", "price_cents": 5000, "description": "Extra opportunity slot for Starter tier"},
    {"tier": "GROWTH", "price_cents": 4000, "description": "Extra opportunity slot for Growth tier"},
    {"tier": "PRO", "price_cents": 3500, "description": "Extra opportunity slot for Pro tier"},
    {"tier": "TEAM", "price_cents": 3000, "description": "Extra opportunity slot for Team tier"},
    {"tier": "BUSINESS", "price_cents": 2500, "description": "Extra opportunity slot for Business tier"},
    {"tier": "ENTERPRISE", "price_cents": 2000, "description": "Extra opportunity slot for Enterprise tier"},
]


def create_subscription_products():
    """Create all subscription products and prices in Stripe"""
    client = get_stripe_client()
    
    print("\n=== Creating OppGrid Subscription Products ===\n")
    
    created_prices = {}
    
    for tier in SUBSCRIPTION_TIERS:
        print(f"Creating {tier['name']}...")
        
        existing_price_id = os.getenv(f"STRIPE_PRICE_{tier['tier_key']}")
        if existing_price_id:
            print(f"  -> Already exists: {existing_price_id}")
            created_prices[tier['tier_key']] = existing_price_id
            continue
        
        try:
            product = client.Product.create(
                name=tier['name'],
                description=tier['description'],
                metadata={
                    "tier": tier['tier_key'].lower(),
                    "type": "subscription"
                }
            )
            print(f"  -> Product created: {product.id}")
            
            price = client.Price.create(
                product=product.id,
                unit_amount=tier['price_cents'],
                currency="usd",
                recurring={"interval": "month"},
                metadata={
                    "tier": tier['tier_key'].lower(),
                    "type": "subscription"
                }
            )
            print(f"  -> Price created: {price.id}")
            
            created_prices[tier['tier_key']] = price.id
            
        except Exception as e:
            print(f"  -> ERROR: {e}")
    
    print("\n=== Subscription Products Summary ===\n")
    print("Add these to your environment variables:\n")
    for tier_key, price_id in created_prices.items():
        print(f"STRIPE_PRICE_{tier_key}={price_id}")
    
    return created_prices


def create_slot_addon_product():
    """Create the slot add-on product with tier-specific prices"""
    client = get_stripe_client()
    
    print("\n=== Creating Slot Add-on Products ===\n")
    
    product = client.Product.create(
        name="OppGrid Extra Opportunity Slot",
        description="Purchase additional opportunity slots for your account",
        metadata={
            "type": "slot_addon"
        }
    )
    print(f"Slot Add-on Product created: {product.id}")
    
    created_prices = {}
    
    for addon in SLOT_ADDON_PRICES:
        try:
            price = client.Price.create(
                product=product.id,
                unit_amount=addon['price_cents'],
                currency="usd",
                metadata={
                    "tier": addon['tier'].lower(),
                    "type": "slot_addon"
                }
            )
            print(f"  -> {addon['tier']} slot price: {price.id} (${addon['price_cents']/100})")
            created_prices[addon['tier']] = price.id
            
        except Exception as e:
            print(f"  -> ERROR creating {addon['tier']} slot price: {e}")
    
    print("\n=== Slot Add-on Prices Summary ===\n")
    print("Add these to your environment variables:\n")
    for tier_key, price_id in created_prices.items():
        print(f"STRIPE_SLOT_PRICE_{tier_key}={price_id}")
    
    return created_prices


def main():
    print("=" * 60)
    print("OppGrid Stripe Product Setup")
    print("=" * 60)
    
    client = get_stripe_client()
    if not client:
        print("ERROR: Stripe client not configured. Check STRIPE_SECRET_KEY.")
        sys.exit(1)
    
    subscription_prices = create_subscription_products()
    slot_prices = create_slot_addon_product()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Copy the price IDs above to your Replit secrets")
    print("2. Restart the backend server")
    print("3. Test the checkout flow on /pricing")


if __name__ == "__main__":
    main()
