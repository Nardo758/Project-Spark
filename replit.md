# OppGrid - Opportunity Intelligence Platform

## Overview
OppGrid is an AI-powered opportunity intelligence platform designed to help users discover, validate, and act on business opportunities. It provides a structured approach from identifying market frictions to connecting users with experts and resources. The platform aims to be an "AI Startup Factory," offering AI-driven analysis, expert marketplaces, subscription-based content gating, and pay-per-unlock features to foster innovation and entrepreneurial success.

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
*   **Monetization & Access Control:** Implements a tiered subscription model (Pro, Business, Enterprise) with time-decay access control and content gating, including one-time purchases (pay-per-unlock, add-ons).
*   **AI Engine:** Integrates with LLMs for AI-powered idea generation, validation, expert matching, and detailed opportunity analysis. An AI Orchestrator service routes tasks between different LLMs.
*   **Authentication:** Uses Replit's OIDC patterns with database-backed user authentication, supporting various providers and PKCE flow, including LinkedIn OAuth.
*   **User Interface:** Features a professional design with a dark theme, deep dive console, dynamic navigation, and interactive mapping with Leaflet.js.
*   **Admin Panel:** Provides tools for user management, subscription control, opportunity moderation, platform statistics, and lead management.
*   **Automated Data Pipeline:** A daily scheduler automates data scraping, import, and AI analysis. Includes a webhook-driven data ingestion pipeline for external sources with a webhook gateway.
*   **Signal-to-Opportunity Algorithm:** An 8-stage processing pipeline converts raw scraped signals into validated business opportunities, including pattern matching, clustering, validation scoring, and market size estimation, categorizing opportunities into confidence tiers.
*   **Data Lifecycle Management:** Ensures complete signal traceability and processing tracking, retaining all data indefinitely for historical pattern discovery.
*   **Payments & Transactions:** Integrates Stripe for payment processing, subscription management, and pay-per-unlock. Includes a `SuccessFeeAgreement` infrastructure for expert services.
*   **Opportunity Analysis & Reporting:** AI generates opportunity scores, market size estimates, and business model suggestions. A Consultant Studio offers a three-path validation system, and a report tracking system logs usage.
*   **Design Thinking Report Framework:** Opportunity Detail pages are structured in tiers (FREE, PRO, BUSINESS) based on the Design Thinking process, covering problem detail, research dashboard, and deep dive with AI.
*   **Unified Opportunity Hub:** For paid users, combines Research and Workspace capabilities with a visual journey timeline, stage-specific guidance, and automatic workspace creation.
*   **AI Co-Founder:** A conversational AI assistant integrated into the Opportunity Hub provides stage-aware guidance, with persistent chat history.
*   **Tool Recommendations Engine:** A curated database of execution tools categorized for various business functions.
*   **Business Formation Guide:** Comprehensive guidance for launching a real business, covering entity types, formation instructions, legal compliance, and financial setup.
*   **Leads Marketplace & Network Hub:** Dedicated platforms for a leads marketplace and connecting users with experts, investors, partners, and lenders.
*   **Expert Recommendation Engine:** An intelligent matching system recommends experts for each opportunity using a weighted scoring algorithm based on category, skills, success metrics, availability, and rating.
*   **Email Automation:** Utilizes an email service for transactional emails, welcome sequences, and status updates with a template system.

## External Dependencies
*   **PostgreSQL:** Managed database provided by Replit.
*   **Stripe:** Payment gateway for subscriptions, pay-per-unlock, and expert service transactions.
*   **Resend:** Email service for transactional emails and automation.
*   **Apify:** Web scraping platform for daily automated data collection.
*   **SerpAPI:** Google Search and Google Maps Reviews API for location-based business intelligence, including a comprehensive Google Scraping Framework.
*   **OpenAI/Anthropic (LLMs):** Integrated for various AI capabilities (e.g., Claude-Haiku, Claude-Sonnet).
*   **LinkedIn OAuth:** Integrated for professional network authentication.

## Recent Changes (December 2024)

### Tiered Report Framework (December 25, 2024)
*   **ReportGenerator Service:** Backend service (`backend/app/services/report_generator.py`) for generating tiered opportunity reports with tier entitlement checks
*   **Layer 1 - Problem Overview:** Pro+ access, includes Executive Summary, Problem Statement, Market Snapshot, Validation Signals, Key Risks, Next Steps ($15 one-time or Pro subscription)
*   **Layer 2 - Deep Dive Analysis:** Business+ access, adds TAM/SAM/SOM, Demographic Deep Dive (Census data), Competitive Landscape, Geographic Analysis
*   **Layer 3 - Execution Package:** Business (5/mo limit) or Enterprise (unlimited), full Business Plan, Go-to-Market Strategy (3 phases), Financial Projections (3-year), 90-Day Roadmap, Risk Mitigation Plan
*   **Report Types:** Added `LAYER_1_OVERVIEW`, `LAYER_2_DEEP_DIVE`, `LAYER_3_EXECUTION` to ReportType enum
*   **API Endpoints:** POST `/api/v1/reports/opportunity/{id}/layer1`, `/layer2`, `/layer3` with proper entitlement checks
*   **Rolling Limits:** Business tier has 5 Layer 3 reports per rolling 30-day period, Enterprise unlimited
*   **Frontend ReportViewer:** Modal component (`frontend/src/components/ReportViewer.tsx`) with layer tabs, tier-based access, and PDF download via browser print
*   **Pay-per-unlock Support:** Layer 1 reports accessible to Free users who paid $15 opportunity unlock

### Census & Demographics Integration (December 25, 2024)
*   **Database Schema:** Added `demographics` and `search_trends` JSONB columns to opportunities table with `demographics_fetched_at` timestamp
*   **CensusDataService:** Backend service for Census Bureau ACS 5-Year API with 16 demographic variables (population, income, age, education, unemployment, housing, commute)
*   **GoogleTrendsService:** Backend service for DMA-level search demand data via SerpAPI
*   **Demographics Endpoint:** `/api/opportunities/{id}/demographics` with Business+ tier gating, returns combined Census + Trends data
*   **Enhanced Signal Scoring:** Algorithm applies demographic multipliers (population, income, underserved bonus) to base opportunity scores
*   **Research Dashboard Tabs:** Geographic Insights, Problem Analysis, Market Sizing tabs in OpportunityDetail.tsx
*   **State FIPS Mapping:** Utility function for Census API geographic queries
*   **Key Census Variables:** B01003 (population), B19013 (median income), B01002 (age), B11001 (households), B17001 (poverty), B23025 (unemployment), B25077 (home value), B25064 (rent), B15003 (education)

### Opportunity Detail Page Enhancements
*   **Time-Based Access Controls:** Header now displays freshness badges (HOT, WARM, MATURE, ARCHIVE) and unlock timing ("Unlocks for your tier in X days" or "Unlocked")
*   **Problem Statement Section:** Moved to standalone section above Problem Detail with violet theme
*   **CTA Updates:** All WorkHub buttons now say "Deep Dive WorkHub" with proper auth guards for pay-per-unlock
*   **Payment Integration:** Pay-per-unlock buttons appear for eligible users with Stripe integration

### Opportunity Card Improvements
*   **Consistent Scores:** All cards use deterministic fallback formula `(70 + opp.id % 20)` for scores
*   **Market Size Rounding:** Displays rounded values with ~ prefix (e.g., ~$132M instead of $131.5M)
*   **Description Display:** Cards skip "Market Opportunity Overview" header and show actual analysis content
*   **Unlock Status Badges:** Cards show "Unlocks in Xd" or "Unlocked" based on tier access

### UI Cleanup
*   Removed "Open Hub" redundant text from clickable cards
*   Removed Trending/Low Competition badges from detail header, replaced with access status
*   Standardized fallback chain: description → ai_summary → "Analysis pending..."

### Quick Validation Metrics (December 2024)
*   **Title Case Formatting:** `titleCase()` function capitalizes each word (e.g., "small businesses" → "Small Businesses")
*   **Consistent Card Sizing:** All metrics use `text-xl` with centered text and `bg-stone-50` backgrounds
*   **Optimized Grid Layout:** `[1fr_1fr_1.5fr_0.75fr]` - wider Target Audience, narrower Feasibility
*   **Consistent Section Headers:** All subsections use `text-lg font-bold mb-4` styling

### Access Control Updates (December 2024)
*   **Unified Access Logic:** Both header and "Ready to Deep Dive?" CTA sections use same time-decay access control
*   **Access Priority:** `is_accessible` → Pay-per-unlock → Days until unlock → Upgrade prompt
*   **CTA Text Updated:** "Ready to Deep Dive?" with contextual buttons based on user access state

## Future Features (To Circle Back)
*   **Personal AI Knowledge Base (Brain Dashboard):** Transform the "My AI Co-founder" section (`/brain`) into a personal knowledge repository where users can upload their own data (resume, skills, industry experience, past business plans, preferences). This data would be used to personalize AI Co-Founder responses across all opportunities the user works on. Features to build: document upload/storage, knowledge processing/indexing, AI context injection, user preference settings, daily training questions.