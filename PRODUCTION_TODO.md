# OppGrid Production Deployment Checklist

## Environment & Secrets

- [ ] **STRIPE_WEBHOOK_SECRET** - Add to secrets (get from Stripe Dashboard > Webhooks)
- [ ] **SESSION_SECRET** - Generate secure random string for JWT signing
- [ ] **APIFY_API_KEY** - For automated opportunity scraping (if using scheduler)
- [ ] Configure Stripe webhook endpoint URL in Stripe Dashboard pointing to `/api/v1/webhook/stripe`

## Database

- [ ] Run Alembic migrations: `cd backend && alembic upgrade head`
- [ ] Verify all tables created: users, subscriptions, opportunities, transactions, success_fee_agreements, milestones, expert_bookings
- [ ] Seed initial expert data if needed

## Stripe Configuration

- [ ] Create subscription products & prices in Stripe:
  - Pro: $99/month
  - Business: $499/month
  - Enterprise: Custom pricing
- [ ] Set environment variables:
  - `STRIPE_PRICE_PRO` - Stripe price ID for Pro tier
  - `STRIPE_PRICE_BUSINESS` - Stripe price ID for Business tier
- [ ] Configure pay-per-unlock price ($15)
- [ ] Test webhook delivery in Stripe Dashboard

## Authentication

- [ ] Verify Replit Auth is configured
- [ ] Test all login flows (Google, GitHub, X, Apple, Email)
- [ ] Verify session persistence across page refreshes

## API Endpoints to Verify

- [ ] `/api/v1/auth/*` - Authentication flows
- [ ] `/api/v1/opportunities/*` - Opportunity CRUD
- [ ] `/api/v1/subscriptions/*` - Subscription management
- [ ] `/api/v1/experts/*` - Expert matching & booking
- [ ] `/api/v1/agreements/*` - Success-fee agreements
- [ ] `/api/v1/milestones/*` - Milestone tracking
- [ ] `/api/v1/webhook/stripe` - Payment webhooks

## Frontend Pages to Test

- [ ] Homepage (index.html) - Hero, navigation, opportunity cards
- [ ] Discover (discover.html) - Browse opportunities with filters
- [ ] Idea Engine (`/idea-engine`) - AI idea generation & validation
- [ ] Expert Marketplace (expert-marketplace.html) - Browse & filter experts
- [ ] Expert Checkout (expert-checkout.html) - Book expert services
- [ ] AI Match (ai-match.html) - AI-powered expert matching
- [ ] AI Roadmap (ai-roadmap.html) - AI-generated startup roadmap
- [ ] Profile Onboarding (profile-onboarding.html) - New user setup
- [ ] Pricing (pricing.html) - Subscription tiers
- [ ] Admin Panel (admin.html) - Admin controls

## Performance & Security

- [ ] Enable HTTPS (automatic on Replit deployments)
- [ ] Verify CORS configuration for production domain
- [ ] Test rate limiting on API endpoints
- [ ] Audit for exposed secrets in client-side code
- [ ] Enable production logging level

## Advanced Features (Future)

- [ ] Implement automated escrow release scheduler (30-day holds)
- [ ] Add Stripe Connect for direct expert payouts
- [ ] Set up email notifications via Resend for:
  - Payment confirmations
  - Milestone approvals
  - Agreement triggers
- [ ] Implement scheduled opportunity import from Apify
- [ ] Add analytics tracking

## Pre-Launch Testing

- [ ] Complete end-to-end user flow: signup -> browse -> validate idea -> book expert
- [ ] Test subscription upgrade/downgrade flows
- [ ] Test pay-per-unlock flow
- [ ] Verify mobile responsiveness
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)

## Deployment

- [ ] Click "Publish" in Replit to deploy
- [ ] Verify production database connection
- [ ] Test all critical flows on production URL
- [ ] Monitor logs for errors
