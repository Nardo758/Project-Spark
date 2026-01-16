# OppGrid - Opportunity Intelligence Platform

## Overview
OppGrid is an AI-powered opportunity intelligence platform designed to help users discover, validate, and act on business opportunities. It provides a structured approach from identifying market frictions to connecting users with experts and resources. The platform aims to be an "AI Startup Factory," offering AI-driven analysis, expert marketplaces, subscription-based content gating, and pay-per-unlock features to foster innovation and entrepreneurial success, with a vision to democratize access to high-quality business intelligence.

## User Preferences
I want iterative development, with a focus on delivering core features quickly and refining them based on feedback. Prioritize modular and reusable code. I prefer clear, concise explanations and direct answers. Ask before making major architectural changes or introducing new external dependencies. Do not make changes to the `replit.nix` file.

## System Architecture
OppGrid utilizes a modern hybrid architecture with a React 18 frontend (Vite, TailwindCSS) on Port 5000 and a Python FastAPI backend (SQLAlchemy ORM) on Port 8000, backed by a Replit PostgreSQL database. Client-side state is managed with Zustand, and routing with React Router v6. The frontend proxies `/api/*` requests to the backend.

**Key Architectural Decisions & Features:**
*   **Monetization & Access Control:** Implements a 3-gate revenue model:
    - **Gate 1 - Platform Access (Subscription):** 6-tier dual-track pricing:
      - Individual Track: Starter ($20/mo, 1 slot), Growth ($50/mo, 3 slots), Pro ($99/mo, 5 slots)
      - Business Track: Team ($250/mo, 5 slots, 3 seats), Business ($750/mo, 15 slots, 10 seats), Enterprise ($2,500+/mo, 30 slots, unlimited seats)
    - **Gate 2 - Opportunity Slots:** Monthly credits with exclusivity caps (3-10 users per opportunity). Additional slots purchasable at tier-specific prices ($20-$50).
    - **Gate 3 - Execution Reports:** 20 AI-generated report types with tier-based discounts (0%/10%/15%/20%/50%). Business track includes white-label reports and commercial use rights.
    - Report bundles: Marketing ($599), Launch ($899), Complete Starter ($1,299) with 20-30% savings.
*   **Team Seats Management:** Business Track subscribers can manage team members with role-based access (owner/admin/member). Seat limits enforced by tier (Team: 3, Business: 10, Enterprise: unlimited). Includes invitation system with token-based acceptance and member management.
*   **White-Label Reports:** Business Track users can customize report branding with team logo, company name, primary color, and website. Branding is automatically injected into all AI-generated reports via `branding_service.py`. Endpoints: `GET/PATCH /api/teams/{team_id}/branding`, `GET /api/teams/{team_id}/branding/preview`.
*   **AI Engine:** Integrates with Large Language Models (LLMs) for idea generation, validation, expert matching, and detailed opportunity analysis, orchestrated by an AI service.
*   **Authentication:** Uses Replit's OIDC patterns with database-backed user authentication, supporting various providers including LinkedIn OAuth.
*   **User Interface:** Features a professional dark-themed design with a deep dive console, dynamic navigation, and interactive mapping (Leaflet.js/Mapbox).
*   **Admin Panel:** Provides comprehensive tools for user, subscription, opportunity, and lead management, along with platform statistics.
*   **Content Moderation System:** Quality control workflow requiring admin approval before opportunities are publicly visible. Features include:
    - Moderation statuses: pending_review, approved, rejected, needs_edit
    - Admin moderation queue with filtering by status
    - Side-by-side comparison of AI-processed content vs raw source data
    - Inline editing for title, description, and category corrections
    - All public endpoints filter by moderation_status == 'approved'
    - Reprocessed opportunities automatically enter pending_review state
*   **Automated Data Pipeline:** A daily scheduler automates data scraping, import, and AI analysis. Includes a webhook-driven data ingestion pipeline for external sources.
*   **Signal-to-Opportunity Algorithm:** An 8-stage processing pipeline converts raw signals into validated business opportunities, categorized into confidence tiers based on pattern matching, clustering, validation scoring, and market size estimation.
*   **Data Lifecycle Management:** Ensures complete signal traceability and indefinite data retention for historical pattern discovery.
*   **Payments & Transactions:** Integrates Stripe for payment processing, subscription management, and pay-per-unlock, including a `SuccessFeeAgreement` infrastructure for expert services.
*   **Opportunity Analysis & Reporting:** AI generates opportunity scores, market size estimates, and business model suggestions. A Consultant Studio offers a four-path validation system, and a report tracking system logs usage.
    - **Consultant Studio Paths:** (1) Validate Idea - Online vs Physical decision engine, (2) Search Ideas - Database exploration with trend detection, (3) Identify Location - Geographic intelligence with natural language input and AI category inference, (4) Clone Success - Replicate successful business models by analyzing demographics and finding similar markets with configurable radius (3-mile default, 5-mile extended), (5) Report Library - AI-generated business reports.
    - **Report Library:** A comprehensive library of 20 AI-generated report templates organized into 5 categories (Popular, Marketing, Product, Business, Research). Reports include Ad Creatives, Brand Package, Landing Page, Content Calendar, Email Funnel, Sales Funnel, User Personas, Feature Specs, MVP Roadmap, PRD, GTM Strategy, KPI Dashboard, Pricing Strategy, Competitive Analysis, Customer Interview Guide, and more. Requires PRO+ subscription tier. Accessible from Consultant Studio and WorkHub toolkit panel.
    - **Real-time Analysis Timer:** Frontend displays countdown timer during AI analysis (starts at 15s, shows "Processing..." if exceeds estimate).
    - **Premium Deep Clone Analysis:** Paid feature ($49) for detailed target city analysis with side-by-side 3-mile and 5-mile radius comparison showing population, income, competition, households, and growth rate metrics.
*   **Design Thinking Report Framework:** Opportunity Detail pages are structured in tiers (FREE, PRO, BUSINESS) based on the Design Thinking process, incorporating AI-generated content across problem detail, research dashboard, and deep dive sections. Reports integrate satellite maps, Census data, and Google Trends via AI-powered generation methods.
*   **Unified Opportunity Hub:** For paid users, combines Research and Workspace capabilities with a visual journey timeline, stage-specific guidance, and automatic workspace creation.
*   **AI Co-Founder (WorkHub):** A chat-first conversational AI assistant with 4-stage workflow (Validate/Research/Plan/Execute). Features include:
    - Left collapsible context panel with opportunity summary, tasks, and expert recommendations
    - Stage-aware quick actions and toolkit panels (Formation Guide, Tool Stack, Funding, Expert Connect)
    - Inline card rendering for checklists and structured AI responses
    - Paid report CTAs that auto-trigger on keywords
    - Mobile responsive with drawer-style left panel
    - **BYOK (Bring Your Own Key):** Users can connect their own Anthropic Claude API key via settings modal. Keys are validated and stored encrypted (Fernet/PBKDF2). AI requests use user's key when available, falling back to platform key. Response includes `key_source` for tracking.
*   **Tool Recommendations Engine:** A curated database of execution tools categorized for various business functions.
*   **Business Formation Guide:** Comprehensive guidance for launching a real business, covering entity types, formation instructions, legal compliance, and financial setup.
*   **Leads Marketplace & Network Hub:** Dedicated platforms for a leads marketplace and connecting users with experts, investors, partners, and lenders.
*   **Expert Recommendation Engine:** An intelligent matching system recommends experts using a weighted scoring algorithm based on category, skills, success metrics, availability, and rating.
*   **Expert Collaboration System:** Facilitates interactions between clients and verified experts through structured engagements, milestones, in-platform messaging, session scheduling, and post-engagement reviews, supporting various engagement types and permission levels.
    - **Stripe Connect Integration:** 85/15 revenue split with automatic expert payouts via Stripe Connect. Platform fee calculated via `calculate_platform_split()`, stored in engagement records. Expert onboarding flow with account creation, status tracking, and earnings dashboard.
    - **Expert Dashboard:** Comprehensive view at `/expert/dashboard` with earnings summary, client management, and Stripe Connect status. Three-tab interface (Overview, Clients, Earnings) with callback handling for Connect onboarding completion.
    - **Rating & Review System:** Post-engagement review modal with 5-star ratings (overall, expertise, communication, responsiveness, value), text review, and recommendation toggles. Reviews update expert `avg_rating` and `total_reviews` for matching algorithm.
    - **LinkedIn Expert Onboarding:** Expert application flow at `/expert/apply` with LinkedIn OAuth auto-population. Form pre-fills name, email, and avatar from LinkedIn profile, allowing experts to complete category selection, specializations, skills, hourly rate, and availability before submission.
    - **External Expert Integration:** Admin tool at `/admin/experts` for importing Upwork freelancers via API. Supports search by category/keyword, individual import, and bulk sync. External experts display with "Upwork" badge in marketplace and link to external profiles.
*   **Email Automation:** Utilizes an email service for transactional emails, welcome sequences, and status updates with a template system.

## External Dependencies
*   **PostgreSQL:** Managed database provided by Replit.
*   **Stripe:** Payment gateway for subscriptions, pay-per-unlock, and expert service transactions.
*   **Resend:** Email service for transactional emails and automation.
*   **Apify:** Web scraping platform for automated data collection.
*   **SerpAPI:** Google Search and Google Maps Reviews API for location-based business intelligence, including a comprehensive Google Scraping Framework.
*   **OpenAI/Anthropic (LLMs):** Integrated for various AI capabilities (e.g., Claude-Haiku, Claude-Sonnet).
*   **LinkedIn OAuth:** Integrated for professional network authentication.
*   **Census Bureau ACS 5-Year API:** Provides demographic data for opportunity analysis.
*   **Mapbox:** Used for map visualizations.
*   **SBA (Small Business Administration):** Curated SBA loan program data and financing course information for the Funding Discovery feature at `/funding`.