# OppGrid - Opportunity Intelligence Platform

## Recent Changes (December 2024)

- **Time-Decay Pricing & Pay-Per-Unlock** (December 17, 2024):
  - NEW: Time-decay access control based on opportunity age (per pricing strategy document)
    - Enterprise: Real-time (0+ days)
    - Business: Fresh (8+ days) 
    - Pro: Validated (31+ days)
    - Free: Archive (91+ days, pay-per-unlock)
  - NEW: `/api/v1/subscriptions/pay-per-unlock` - Create payment intent for $15 unlock
  - NEW: `/api/v1/subscriptions/confirm-pay-per-unlock` - Confirm payment and grant 30-day access
  - NEW: `/api/v1/subscriptions/access/{opportunity_id}` - Get detailed access info with freshness badge
  - NEW: `/api/v1/subscriptions/stripe-key` - Get Stripe publishable key for frontend
  - Updated tier pricing: Pro $99/mo, Business $499/mo, Enterprise $2,500+/mo
  - Age badges on opportunity cards: 🔥 HOT, ⚡ FRESH, ✓ VALIDATED, 📚 ARCHIVE
  - Countdown timers showing days until opportunity unlocks for user's tier
  - Pay-per-unlock flow with Stripe Elements integration
  - UnlockedOpportunity model updated with: unlock_method, amount_paid, stripe_payment_intent_id, expires_at
  - Daily rate limit: 5 pay-per-unlocks per day for free tier

- **Access Control & Admin Panel** (December 16, 2024):
  - NEW: `admin.html` - Full admin panel with dashboard, user management, opportunity moderation, and subscription controls
  - NEW: Subscription tier access control dependencies (`require_pro`, `require_business`, `require_enterprise`)
  - NEW: `/api/v1/admin/subscriptions` - List and filter all subscriptions
  - NEW: `/api/v1/admin/subscriptions/{id}/tier` - Manually update subscription tier
  - NEW: `/api/v1/admin/users/{id}/grant-subscription` - Grant subscription to user
  - NEW: `/api/v1/admin/users/{id}/demote` - Remove admin privileges
  - Admin panel features: Platform stats, user search/filter, ban/unban users, promote/demote admins
  - Opportunity management: View, search, and delete opportunities
  - Subscription management: View all subscriptions, change tiers, grant access
  - Report moderation: View pending reports, resolve or dismiss
  - Frontend access control: Admin-only page with token verification and redirect

- **Stripe & Resend Integration** (December 16, 2024):
  - Connected Stripe sandbox via Replit connector for payment processing
  - Connected Resend via Replit connector for transactional emails
  - Both services use Replit connector API for secure key management

- **Idea Engine - AI-Powered Idea Generation & Validation** (December 16, 2024):
  - NEW: `/api/v1/idea-engine/generate` - Free AI idea generation and refinement
  - NEW: `/api/v1/idea-engine/validate` - Paid comprehensive idea validation ($9.99)
  - NEW: `/api/v1/idea-engine/create-payment-intent` - Stripe payment intent creation
  - NEW: `/api/v1/idea-engine/stripe-key` - Stripe publishable key endpoint
  - NEW: `idea-engine.html` - 3-step wizard UI (input → generation → validation)
  - Business model pivot: Free idea generation, paid validation service
  - Updated navigation across all pages to include "Idea Engine" link
  - Updated hero CTA to "Validate Your Idea" pointing to Idea Engine
  - Uses claude-haiku-4-5 for fast free generation, claude-sonnet-4-5 for deep validation

- **Rebranding to OppGrid** (December 15, 2024):
  - Updated logo across all pages with new grid-based animated design
  - Violet (#7c3aed) active cells with hover animation (matches site accent color)
  - Roboto Mono font for brand text
  - Updated all page titles from "Katalyst" to "OppGrid"

- **AI-Powered Opportunity Analysis & Tiered Monetization** (December 15, 2024):
  - Created `/api/v1/ai-analysis/` endpoints for AI-powered opportunity analysis
  - AI generates: opportunity scores (0-100), market size estimates, competition levels, business model suggestions
  - Updated Opportunity model with AI analysis fields (ai_analyzed, ai_opportunity_score, ai_summary, etc.)
  - Added "Top Curated Opportunities" featured section on discover page
  - AI badges and insights displayed on opportunity cards
  - Competition level badges (low/medium/high) and viewer count urgency indicators
  - Subscription-based content gating on opportunity detail page
  - Paywall overlays for Research and Deep Dive sections for free users
  - Unlock functionality for individual opportunities with view quota tracking
  - Added `/api/v1/subscriptions/my-subscription` endpoint for frontend subscription status
  - **Server-side gating enforced**: Opportunity detail endpoint now returns gated content based on unlock status
  - Premium AI fields (business_model_suggestions, competitive_advantages, key_risks, next_steps) hidden from non-unlocked users
  - Added `OpportunityGatedResponse` schema with is_unlocked and is_authenticated flags
  - Optional authentication dependency (`get_current_user_optional`) for public access with personalized gating

- **Daily Automated Data Pipeline** (December 15, 2024):
  - Created `backend/scheduler.py` for automated daily syncs
  - Scheduler can trigger Apify scraper, wait for completion, import data, and run AI analysis
  - Added `/api/v1/webhook/apify/trigger-scrape` endpoint to manually trigger scraper
  - Configured scheduled deployment for daily execution
  - Searches for pain points: "frustrated with", "wish there was", "why is it so hard to", etc.

- **Apify Webhook Integration** (December 14, 2024):
  - Created `/api/v1/webhook/apify` endpoint to receive scraped Reddit data
  - `/api/v1/webhook/apify/fetch-latest` - Pull latest data from Apify without webhook
  - Auto-categorizes posts into opportunity categories
  - Calculates severity based on upvotes/comments/frustration keywords
  - Added source tracking columns (source_id, source_url, source_platform) to opportunities

- **Browse Opportunities Flow Fix** (December 14, 2024):
  - Fixed "Browse Opportunities" hero button to link to discover.html instead of opportunity.html
  - Complete user flow now works: Landing → Discovery Feed → Opportunity Detail

- **Deep Dive Console Improvements** (December 13, 2024):
  - Dark Mode toggle with CSS custom properties and localStorage persistence
  - Keyboard Shortcuts: Cmd+Enter to send, Cmd+S to save, arrow keys for navigation, Escape to close panels
  - Message Actions: Copy, bookmark (with persistence), expand/collapse for long messages
  - Saved Threads Panel: Slide-out drawer to view, load, and delete saved conversations
  - Animated Celebration: Overlay animation when all 9 analysis sections completed
  - Export Templates: Markdown, JSON, and Plain Text exports for conversations
  - Share Analysis: Modal with shareable link generation and copy functionality
  - Save to Project: Panel for managing projects and saving opportunities to them
- **Complete Frontend Redesign**: Rebranded from "Friction" to "Katalyst" with new design system
- **New Pages Built**: discover.html, submit.html, pricing.html, signup.html, signin.html, account.html
- **Design System**: Spectral/Inter fonts, stone color palette, violet/purple accents
- **Consistent Navigation**: Home, Browse Ideas, Pricing, Sign In, Get Started across all pages
- **Database Configuration Simplified**: Now uses PG* variables from .replit file (PGHOST=db, PGDATABASE=replit, PGUSER=replit)
- **Resend Integration**: Email service configured via Replit connector - automatically fetches API keys from connector or falls back to environment variables
- **Stripe Integration**: Payment processing configured via Replit connector - automatically fetches API keys from connector or falls back to environment variables  
- **Database Migration**: Added missing user columns (oauth_provider, oauth_id, bio, avatar_url, is_admin, etc.)
- **Model Import Fix**: Fixed WatchlistItem mapper error by updating models/__init__.py import order

## 🚀 Quick Start on Replit

This project is fully configured for Replit deployment!

### Get Started in 3 Steps:

1. **Enable PostgreSQL Database**
   - Click Tools → Database → PostgreSQL → Enable
   - Database URL is automatically configured

2. **Click Run**
   - The app will auto-install dependencies and start
   - Frontend + Backend run together seamlessly

3. **Access Your App**
   - Open the webview to see your application
   - API docs available at `/docs`

### Optional Configuration

Add these secrets in Tools → Secrets for additional features:
- `RESEND_API_KEY` - Email notifications
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET` - Google OAuth
- `GITHUB_CLIENT_ID` & `GITHUB_CLIENT_SECRET` - GitHub OAuth

**📖 Full Documentation**: See [REPLIT_DEPLOYMENT.md](./REPLIT_DEPLOYMENT.md)

---

## Architecture

- **Frontend**: Static HTML/CSS/JavaScript (Port 5000 → External Port 80)
- **Backend**: Python FastAPI (Port 8000 - internal only)
- **Database**: Replit PostgreSQL (Managed)
- **Proxy**: Frontend proxies `/api/*` requests to backend

## Project Structure

```
├── .replit              # Replit configuration
├── replit.nix           # Nix dependencies
├── server.py            # Main entry point (starts both services)
├── backend/             # FastAPI backend
│   ├── app/
│   │   ├── core/        # Configuration, security
│   │   ├── db/          # Database setup
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routers/     # API routes (auth, opportunities, etc.)
│   │   └── schemas/     # Pydantic schemas
│   ├── init_db.py       # Database initialization
│   └── requirements.txt # Python dependencies
├── js/                  # Frontend JavaScript
├── css/                 # Frontend CSS
└── *.html               # Frontend pages (index, login, signup, etc.)
```

## Key Features

✨ **User Authentication**
- Email/password registration and login
- OAuth (Google & GitHub)
- Two-factor authentication (2FA/TOTP)
- Password reset with email verification

🎯 **Opportunity Management**
- Create, edit, and discover problems/opportunities
- Search and filter by category, scope, location
- Validate opportunities (upvote system)
- Comment and discuss opportunities
- Personal watchlist

📊 **Analytics**
- Feasibility scoring
- Geographic distribution
- Completion statistics
- Duplicate detection

🔔 **Notifications**
- In-app notifications
- Email notifications (with Resend)
- Activity tracking

## API Endpoints

Access Swagger docs at `/docs` or ReDoc at `/redoc` when running.

**Main endpoints:**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/opportunities` - List opportunities
- `POST /api/v1/opportunities` - Create opportunity
- `GET /api/v1/opportunities/search` - Search opportunities
- And many more...

## Environment Variables

**Auto-configured in .replit:**
- `PGHOST=db` - PostgreSQL host  
- `PGDATABASE=replit` - Database name
- `PGUSER=replit` - Database user
- `REPL_SLUG`, `REPL_OWNER` - For URL generation
- `SECRET_KEY` - JWT signing (change for production)

**Optional (add via Secrets):**
- `RESEND_API_KEY` - Email service API key
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` - Payment processing
- OAuth credentials for Google/GitHub

See [REPLIT_DEPLOYMENT.md](./REPLIT_DEPLOYMENT.md) for complete details.

## Local Development

To run locally (outside Replit):
1. Set up PostgreSQL
2. Copy `.env.example` to `.env` and configure
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python server.py`

## Deployment

Ready to deploy? Click "Deploy" in Replit and choose:
- **Autoscale**: Scales automatically (recommended)
- **Reserved VM**: Dedicated resources

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production best practices.
