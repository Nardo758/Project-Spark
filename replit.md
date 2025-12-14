# Katalyst - Problem Discovery Engine

## Recent Changes (December 2024)

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
