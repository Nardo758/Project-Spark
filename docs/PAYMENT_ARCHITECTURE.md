# OppGrid Payment Architecture

## Overview

OppGrid uses Stripe as the primary payment gateway, integrated via the Replit Stripe connector for secure credential management. The system supports multiple payment types from subscriptions to one-time purchases.

## Payment Gateway Diagram

See [payment-gateway-architecture.mmd](./diagrams/payment-gateway-architecture.mmd) for the Mermaid diagram.

## Payment Gateways

| Gateway | Status | Notes |
|---------|--------|-------|
| Stripe | Primary | Main payment processor |
| Apple Pay | Active | Via Stripe integration |
| Google Pay | Active | Via Stripe integration |
| PayPal | Optional | Future enhancement |

## Payment Types

### Subscription Payments
- **Pro Tier**: $99/month - Validated opportunities (31+ days)
- **Business Tier**: $499/month - Fresh opportunities (8+ days)
- **Enterprise Tier**: $2,500/month - Real-time access (0+ days)

### One-Time Payments
| Type | Price | Description |
|------|-------|-------------|
| Pay-Per-Unlock | $15 | Archive opportunity access (30-day) |
| Deep Dive | $49 | Layer 2 access add-on (Pro tier) |
| Fast Pass | $99 | HOT opportunity early access (Business tier) |
| Micro Payment | Variable | Expert quick tasks |
| Project Payment | Variable | Larger expert engagements |
| Idea Validation | Variable | AI-powered idea analysis |

## Backend Services

### API Endpoints
- `POST /api/v1/payments/micro` - Create micro payment intent
- `POST /api/v1/payments/project` - Create project payment intent
- `POST /api/v1/payments/deep-dive` - Create Deep Dive payment intent
- `POST /api/v1/payments/fast-pass` - Create Fast Pass payment intent
- `POST /api/v1/payments/confirm` - Confirm payment status
- `POST /api/v1/subscriptions/checkout` - Create subscription checkout
- `POST /api/v1/subscriptions/portal` - Access customer portal
- `POST /api/v1/webhook/stripe` - Stripe webhook handler

### Services
- `StripeService` - Core payment operations
- `UsageService` - Tracks usage and entitlements

## Database Tables

| Table | Purpose |
|-------|---------|
| `transactions` | All payment records |
| `subscriptions` | User subscription state |
| `unlocked_opportunities` | One-time access grants |
| `stripe_webhook_events` | Webhook idempotency |
| `pay_per_unlock_attempts` | Unlock attempt tracking |

## Webhook Events Handled

- `payment_intent.succeeded` - Fulfill payment
- `payment_intent.payment_failed` - Handle failure
- `invoice.paid` - Record subscription payment
- `invoice.payment_failed` - Handle failed invoice
- `checkout.session.completed` - Link subscription
- `customer.subscription.updated` - Sync status
- `customer.subscription.deleted` - Cancel subscription
- `checkout.session.expired` - Analytics logging

## Security

- Stripe credentials via Replit connector (auto-rotated)
- Webhook signature verification with STRIPE_WEBHOOK_SECRET
- Idempotent webhook processing via stripe_webhook_events table
- Transaction audit logging

## Future Enhancements

- [ ] Stripe Connect for expert payouts
- [ ] Success Fee escrow implementation
- [ ] PayPal integration
- [ ] Revenue share automation
