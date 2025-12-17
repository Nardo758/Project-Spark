# Stripe Integration Documentation

This document outlines all Stripe touch points in the OppGrid application.

## Overview

The application uses Stripe for:
1. **Subscription Billing** - Monthly subscription plans (Pro, Business, Enterprise)
2. **Pay-Per-Unlock Payments** - One-time payments for unlocking individual opportunities
3. **Customer Portal** - Self-service billing management
4. **Idea Validation Payments** - One-time payments for the idea validation service

---

## Configuration

### Environment Variables / Secrets

| Variable | Description | Required |
|----------|-------------|----------|
| `STRIPE_SECRET_KEY` | Stripe secret API key | Yes |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key for frontend | Yes |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature verification secret | Yes |
| `STRIPE_PRICE_PRO` | Stripe Price ID for Pro tier ($99/mo) | Yes |
| `STRIPE_PRICE_BUSINESS` | Stripe Price ID for Business tier ($499/mo) | Yes |

### Replit Integration

The app supports the Replit Stripe connector which automatically manages credentials:
- File: `backend/app/services/stripe_service.py`
- Function: `get_stripe_credentials()`
- Falls back to environment variables if connector unavailable

---

## Backend Files

### 1. Stripe Service (`backend/app/services/stripe_service.py`)

**Core service class handling all Stripe operations.**

| Function | Description |
|----------|-------------|
| `get_stripe_credentials()` | Retrieves API keys from Replit connector or env vars |
| `get_stripe_client()` | Returns configured Stripe client |
| `init_stripe()` | Initializes Stripe on module load |

**StripeService Class Methods:**

| Method | Stripe API | Description |
|--------|------------|-------------|
| `create_customer()` | `stripe.Customer.create()` | Creates a new Stripe customer |
| `create_checkout_session()` | `stripe.checkout.Session.create()` | Creates subscription checkout session |
| `create_portal_session()` | `stripe.billing_portal.Session.create()` | Creates customer billing portal |
| `cancel_subscription()` | `stripe.Subscription.modify/delete()` | Cancels subscription |
| `reactivate_subscription()` | `stripe.Subscription.modify()` | Reactivates canceled subscription |
| `get_subscription()` | `stripe.Subscription.retrieve()` | Gets subscription details |
| `get_customer()` | `stripe.Customer.retrieve()` | Gets customer details |
| `construct_webhook_event()` | `stripe.Webhook.construct_event()` | Verifies webhook signature |
| `create_payment_intent_for_unlock()` | `stripe.PaymentIntent.create()` | Creates payment for pay-per-unlock |

**Pricing Configuration:**

```python
TIER_LIMITS = {
    SubscriptionTier.FREE: {
        "monthly_views": 10,
        "monthly_unlocks": 0,
        "price": 0
    },
    SubscriptionTier.PRO: {
        "monthly_views": -1,  # Unlimited
        "monthly_unlocks": -1,
        "price": 99
    },
    SubscriptionTier.BUSINESS: {
        "monthly_views": -1,
        "monthly_unlocks": -1,
        "price": 499
    },
    SubscriptionTier.ENTERPRISE: {
        "price": 2500  # Custom pricing
    }
}

PAY_PER_UNLOCK_PRICE = 1500  # $15.00 in cents
```

---

### 2. Subscriptions Router (`backend/app/routers/subscriptions.py`)

**API endpoints for subscription and payment management.**

#### Endpoints

| Endpoint | Method | Description | Stripe API Used |
|----------|--------|-------------|-----------------|
| `/api/v1/subscriptions/stripe-key` | GET | Returns publishable key for frontend | None (reads config) |
| `/api/v1/subscriptions/` | GET | Get billing info | None (reads DB) |
| `/api/v1/subscriptions/my-subscription` | GET | Get current subscription | None (reads DB) |
| `/api/v1/subscriptions/limits` | GET | Get tier limits | None |
| `/api/v1/subscriptions/usage` | GET | Get usage stats | None |
| `/api/v1/subscriptions/checkout` | POST | Create checkout session | `stripe.checkout.Session.create()` |
| `/api/v1/subscriptions/portal` | POST | Create billing portal | `stripe.billing_portal.Session.create()` |
| `/api/v1/subscriptions/cancel` | POST | Cancel subscription | `stripe.Subscription.modify()` |
| `/api/v1/subscriptions/unlock` | POST | Unlock opportunity (subscription) | None |
| `/api/v1/subscriptions/unlocked/{id}` | GET | Check if unlocked | None |
| `/api/v1/subscriptions/access/{id}` | GET | Get access info | None |
| `/api/v1/subscriptions/pay-per-unlock` | POST | Create payment intent | `stripe.PaymentIntent.create()` |
| `/api/v1/subscriptions/confirm-pay-per-unlock` | POST | Confirm payment | `stripe.PaymentIntent.retrieve()` |
| `/api/v1/subscriptions/export` | POST | Export opportunities | None |
| `/api/v1/subscriptions/webhook` | POST | Handle Stripe webhooks | `stripe.Webhook.construct_event()` |

---

### 3. Idea Engine Router (`backend/app/routers/idea_engine.py`)

**Separate payment endpoints for idea validation service.**

| Endpoint | Method | Description | Stripe API Used |
|----------|--------|-------------|-----------------|
| `/api/v1/idea-engine/create-payment-intent` | POST | Create payment intent ($9.99) | `stripe.PaymentIntent.create()` |
| `/api/v1/idea-engine/stripe-key` | GET | Returns publishable key | None (reads config) |

---

## Webhook Events

**Endpoint:** `POST /api/v1/subscriptions/webhook`

### Handled Events

| Event Type | Handler Function | Description |
|------------|------------------|-------------|
| `checkout.session.completed` | `handle_checkout_completed()` | Updates subscription ID after successful checkout |
| `customer.subscription.updated` | `handle_subscription_updated()` | Syncs subscription status, tier, and period dates |
| `customer.subscription.deleted` | `handle_subscription_deleted()` | Resets user to free tier |

### Webhook Handler Functions

```python
def handle_checkout_completed(session, db):
    # Links Stripe subscription ID to user's subscription record

def handle_subscription_updated(stripe_subscription, db):
    # Updates: status, tier, current_period_start, current_period_end, cancel_at_period_end

def handle_subscription_deleted(stripe_subscription, db):
    # Resets to FREE tier, sets status to CANCELED
```

---

## Database Models

### Subscription Model (`backend/app/models/subscription.py`)

**Stripe-related fields:**

| Field | Type | Description |
|-------|------|-------------|
| `stripe_customer_id` | String | Stripe Customer ID |
| `stripe_subscription_id` | String | Stripe Subscription ID |
| `current_period_start` | DateTime | Subscription period start |
| `current_period_end` | DateTime | Subscription period end |
| `cancel_at_period_end` | Boolean | Whether canceling at period end |

### UnlockedOpportunity Model

**Pay-per-unlock tracking:**

| Field | Type | Description |
|-------|------|-------------|
| `stripe_payment_intent_id` | String | Payment intent ID for the unlock |
| `amount_paid` | Integer | Amount paid in cents |
| `unlock_method` | Enum | SUBSCRIPTION or PAY_PER_UNLOCK |
| `expires_at` | DateTime | When pay-per-unlock access expires (30 days) |

---

## Frontend Integration Points

### Initializing Stripe

```javascript
// Fetch publishable key
const response = await fetch('/api/v1/subscriptions/stripe-key');
const { publishable_key } = await response.json();
const stripe = Stripe(publishable_key);
```

### Creating a Subscription Checkout

```javascript
const response = await fetch('/api/v1/subscriptions/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        tier: 'pro',  // or 'business'
        success_url: window.location.origin + '/success',
        cancel_url: window.location.origin + '/pricing'
    })
});
const { url } = await response.json();
window.location.href = url;  // Redirect to Stripe Checkout
```

### Pay-Per-Unlock Flow

```javascript
// Step 1: Create payment intent
const response = await fetch('/api/v1/subscriptions/pay-per-unlock', {
    method: 'POST',
    body: JSON.stringify({ opportunity_id: 123 })
});
const { client_secret } = await response.json();

// Step 2: Confirm payment with Stripe.js
const result = await stripe.confirmCardPayment(client_secret, {
    payment_method: { card: cardElement }
});

// Step 3: Confirm unlock on backend
await fetch('/api/v1/subscriptions/confirm-pay-per-unlock', {
    method: 'POST',
    body: JSON.stringify({ payment_intent_id: result.paymentIntent.id })
});
```

### Opening Customer Portal

```javascript
const response = await fetch('/api/v1/subscriptions/portal', {
    method: 'POST',
    body: JSON.stringify({
        return_url: window.location.origin + '/settings'
    })
});
const { url } = await response.json();
window.location.href = url;
```

---

## Stripe Dashboard Setup Requirements

### Products & Prices

Create the following in Stripe Dashboard:

1. **Pro Plan** - $99/month recurring
   - Set Price ID as `STRIPE_PRICE_PRO`

2. **Business Plan** - $499/month recurring
   - Set Price ID as `STRIPE_PRICE_BUSINESS`

### Webhook Configuration

1. Add webhook endpoint: `https://your-domain.com/api/v1/subscriptions/webhook`
2. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
3. Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`

### Customer Portal Configuration

Enable the following in Stripe Customer Portal settings:
- Update payment methods
- View invoice history
- Cancel subscriptions

---

## Payment Flows Summary

### Subscription Flow

```
User selects plan → POST /checkout → Redirect to Stripe Checkout
    → Payment succeeds → Stripe sends checkout.session.completed webhook
    → Backend updates subscription → User redirected to success_url
```

### Pay-Per-Unlock Flow

```
User clicks unlock → POST /pay-per-unlock → Returns client_secret
    → Frontend confirms with stripe.confirmCardPayment()
    → POST /confirm-pay-per-unlock → Backend verifies & grants access
```

### Idea Validation Flow

```
User submits idea → POST /create-payment-intent → Returns client_secret
    → Frontend confirms payment → Service processes validation
```

---

## Testing

### Test Mode

Use Stripe test keys (`sk_test_...`, `pk_test_...`) for development.

### Test Cards

| Card Number | Scenario |
|-------------|----------|
| 4242424242424242 | Successful payment |
| 4000000000000002 | Declined |
| 4000002500003155 | Requires authentication |

### Webhook Testing

Use Stripe CLI for local testing:
```bash
stripe listen --forward-to localhost:5000/api/v1/subscriptions/webhook
```

---

## Error Handling

All Stripe operations include error handling:
- `ValueError` for missing configuration
- `HTTPException` for API errors
- Logging for debugging

Common errors:
- "Stripe not configured" - API keys not set
- "Payment not completed" - Payment intent status check failed
- "Invalid payment intent" - Signature verification failed
