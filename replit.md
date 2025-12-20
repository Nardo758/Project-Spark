# OppGrid - Opportunity Intelligence Platform

## Overview
OppGrid is an AI-powered opportunity intelligence platform designed to help users discover, validate, and act on business opportunities. It provides a structured approach to identifying market frictions, generating and validating business ideas, and connecting users with experts and resources. The platform aims to be an "AI Startup Factory" by offering a full lifecycle from idea generation to expert-led execution, leveraging AI for analysis, matching, and monetization. Key capabilities include AI-driven opportunity analysis, expert marketplaces, subscription-based content gating, and pay-per-unlock features, all designed to foster innovation and entrepreneurial success.

## User Preferences
I want iterative development, with a focus on delivering core features quickly and refining them based on feedback. Prioritize modular and reusable code. I prefer clear, concise explanations and direct answers. Ask before making major architectural changes or introducing new external dependencies. Do not make changes to the `replit.nix` file.

## System Architecture
OppGrid utilizes a modern hybrid architecture:
- **Frontend:** React 18 + Vite + TailwindCSS (Port 5000)
- **Backend:** Python FastAPI with SQLAlchemy ORM (Port 8000)
- **Database:** Replit PostgreSQL
- **State Management:** Zustand for client-side state
- **Routing:** React Router v6

The frontend proxies `/api/*` requests to the backend via Vite's dev server configuration.

**Key Architectural Decisions & Features:**
*   **Monetization & Access Control:** Implements a tiered subscription model (Pro, Business, Enterprise) with **time-decay access control** for opportunities:
    - **HOT**: 0–7 days
    - **FRESH**: 8–30 days
    - **VALIDATED**: 31–90 days
    - **ARCHIVE**: 91+ days

    Content gating is enforced server-side via entitlements, and one-time purchases can grant access with expiry:
    - **Pay-per-unlock**: $15 (ARCHIVE), **30-day access**, daily limit 5
    - **Deep Dive add-on**: $49 (eligibility by tier / entitlement)
    - **Fast Pass**: $99 (Business tier, HOT single-opportunity access, **30-day access**)
*   **AI Engine:** Integrates with LLMs (e.g., Claude-Haiku, Claude-Sonnet) for AI-powered idea generation, comprehensive idea validation, expert matching, and detailed opportunity analysis (scoring, market size, competition, business models).
*   **Authentication:** Uses Replit's OIDC patterns for secure, database-backed user authentication supporting Google, GitHub, X, Apple, and email logins with PKCE flow.
*   **User Interface:** Features a professional design with a black/dark stone primary accent and complementary semantic colors for badges (e.g., Red for HOT, Green for VALIDATED). The UI includes a deep dive console with dark mode, keyboard shortcuts, message actions, and export capabilities.
*   **Admin Panel:** A comprehensive `admin.html` provides tools for user management, subscription control, opportunity moderation, and platform statistics.
*   **Automated Data Pipeline:** A daily scheduler (`backend/scheduler.py`) automates data scraping (via Apify), import, and AI analysis to keep opportunity data fresh.
*   **Payments & Transactions:** Integrates Stripe for payment processing, subscription management, and pay-per-unlock features. It includes a `SuccessFeeAgreement` infrastructure with milestone tracking and payout splitting for expert services.
*   **Opportunity Analysis:** AI generates opportunity scores, market size estimates, competition levels, and business model suggestions, which are displayed on opportunity cards and detailed pages. Content gating is enforced server-side based on user subscription tiers or unlock status.

## Recent Changes (December 20, 2024)

**Navigation Bar Restructuring (Brain AI Architecture):**
- New navigation structure: [Logo] Discover | Build | Manage | [Project Switcher] | [User]
- Discover dropdown: Opportunity Feed, Validate Idea (Idea Engine)
- Build dropdown: Report Studio, Business Plan, Pitch Deck
- Manage dropdown: My Projects, Saved Ideas, AI Co-founder
- Guest navigation: Discover, Build, Pricing, Sign In, Get Started

**Landing Page Redesign (Dual Entry Points):**
- Explorer path: Search & Discover with search box for browsing AI-curated opportunities
- Ideator path: Build & Validate with textarea for describing business ideas
- Live Platform Metrics sidebar: Validated Ideas, Market Opportunity, Active Markets, Validated Opps
- Trending This Week section with category growth percentages
- Featured Consultant Report Studio CTA with dark gradient section

**Discover Page Enhancements:**
- FRESH/OLD freshness badges based on opportunity age (7 days = FRESH)
- AI Match scores displayed prominently (purple badge with percentage)
- Star ratings based on feasibility score
- Views, saves, and timestamp metrics on each card
- Personal Discovery Metrics sidebar: Ideas Viewed, Avg Match Score, Top Interest, Avg Freshness
- Save/Unsave watchlist functionality restored with visual feedback
- "Generate Report" button links to Consultant Report Studio

**Consultant Report Studio (/build/reports):**
- Report type selection: Feasibility Study, Market Analysis, Strategic Assessment, Progress Report
- Data Sources Integration status with live updating indicators
- Real-Time Validation Metrics grid
- AI-generated Executive Summary with confidence score
- Quick Actions sidebar: Business Plan Generator, Financial Models, Pitch Deck Assistant

**Previous Payment & Access Control Enhancements:**
- Deep Dive add-on ($49): Schema updated with can_buy_deep_dive and deep_dive_price fields
- Enterprise contact modal: New EnterpriseContactModal component
- Subscription reconciliation: Enabled STRIPE_RECONCILE_JOB_ENABLED

## Previous Changes (December 19, 2024)

**DeepSeek Transformation - Navigation & User Flows:**
- Updated navigation with conditional display based on auth state:
  - Guest users: Home, Browse Ideas, Idea Engine, Pricing, Sign In/Get Started
  - Logged-in users (9 items): Dashboard, Discover, Builder (dropdown), Leads, Content, Network, Funding, Tools, Learn
- Builder dropdown contains: Idea Engine, AI Expert Match, AI Roadmap, Expert Marketplace
- New users redirected to Profile Onboarding after signup before accessing dashboard
- Added success-fee/revenue-share infrastructure with transaction record creation
- Payout splitting: 70% expert, 20% escrow (30-day hold), 10% platform

**Personalized Dashboard (dashboard.html):**
- Welcome Bar with AI Match Score and daily opportunity digest
- Quick Actions grid (6 buttons): Find Opportunity, Validate Idea, Generate Leads, Create Business Plan, Find Co-founder, Check Funding
- AI-curated Opportunity Feed with match scores and HOT/FRESH/VALIDATED status badges
- Progress Trackers: Active projects, lead generation stats, content sales metrics
- AI Recommendations: Personalized co-pilot suggestions based on user profile
- Trending in Network: Community activity feed with success stories

## External Dependencies
*   **PostgreSQL:** Managed database provided by Replit.
*   **Stripe:** Payment gateway for subscriptions, pay-per-unlock, and expert service transactions. Integrated via Replit connector.
*   **Resend:** Email service for transactional emails (e.g., password resets, notifications). Integrated via Replit connector.
*   **Apify:** Web scraping platform used for daily automated data collection (e.g., from Reddit).
*   **OpenAI/Anthropic (LLMs):** Integrated for AI capabilities like idea generation, validation, opportunity analysis, and expert matching. Specific models like Claude-Haiku and Claude-Sonnet are used.