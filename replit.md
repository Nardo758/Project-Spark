# OppGrid - Opportunity Intelligence Platform

## Overview
OppGrid is an AI-powered opportunity intelligence platform designed to help users discover, validate, and act on business opportunities. It provides a structured approach to identifying market frictions, generating and validating business ideas, and connecting users with experts and resources. The platform aims to be an "AI Startup Factory" by offering a full lifecycle from idea generation to expert-led execution, leveraging AI for analysis, matching, and monetization. Key capabilities include AI-driven opportunity analysis, expert marketplaces, subscription-based content gating, and pay-per-unlock features, all designed to foster innovation and entrepreneurial success.

## User Preferences
I want iterative development, with a focus on delivering core features quickly and refining them based on feedback. Prioritize modular and reusable code. I prefer clear, concise explanations and direct answers. Ask before making major architectural changes or introducing new external dependencies. Do not make changes to the `replit.nix` file.

## System Architecture
OppGrid utilizes a hybrid architecture with a FastAPI backend (Python) handling business logic, API endpoints, and AI integrations, and a static HTML/CSS/JavaScript frontend for user interaction. The frontend is served on Port 5000 and the backend on Port 8000, with the frontend proxying `/api/*` requests to the backend. Replit's PostgreSQL serves as the primary database.

**Key Architectural Decisions & Features:**
*   **Monetization & Access Control:** Implements a tiered subscription model (Pro, Business, Enterprise) with time-decay access control for opportunities (Hot, Fresh, Validated, Archive). A pay-per-unlock mechanism for archived opportunities is also integrated.
*   **AI Engine:** Integrates with LLMs (e.g., Claude-Haiku, Claude-Sonnet) for AI-powered idea generation, comprehensive idea validation, expert matching, and detailed opportunity analysis (scoring, market size, competition, business models).
*   **Authentication:** Uses Replit's OIDC patterns for secure, database-backed user authentication supporting Google, GitHub, X, Apple, and email logins with PKCE flow.
*   **User Interface:** Features a professional design with a black/dark stone primary accent and complementary semantic colors for badges (e.g., Red for HOT, Green for VALIDATED). The UI includes a deep dive console with dark mode, keyboard shortcuts, message actions, and export capabilities.
*   **Admin Panel:** A comprehensive `admin.html` provides tools for user management, subscription control, opportunity moderation, and platform statistics.
*   **Automated Data Pipeline:** A daily scheduler (`backend/scheduler.py`) automates data scraping (via Apify), import, and AI analysis to keep opportunity data fresh.
*   **Payments & Transactions:** Integrates Stripe for payment processing, subscription management, and pay-per-unlock features. It includes a `SuccessFeeAgreement` infrastructure with milestone tracking and payout splitting for expert services.
*   **Opportunity Analysis:** AI generates opportunity scores, market size estimates, competition levels, and business model suggestions, which are displayed on opportunity cards and detailed pages. Content gating is enforced server-side based on user subscription tiers or unlock status.

## Recent Changes (December 19, 2024)

**DeepSeek Transformation - Navigation & User Flows:**
- Updated navigation with conditional display based on auth state:
  - Guest users: Home, Browse Ideas, Idea Engine, Pricing, Sign In/Get Started
  - Logged-in users: Home, Browse Ideas, Experts, AI Tools (dropdown), Pricing, Dashboard, Account
- AI Tools dropdown contains: Idea Engine, AI Expert Match, AI Roadmap
- New users redirected to Profile Onboarding after signup before accessing dashboard
- Added success-fee/revenue-share infrastructure with transaction record creation
- Payout splitting: 70% expert, 20% escrow (30-day hold), 10% platform

## External Dependencies
*   **PostgreSQL:** Managed database provided by Replit.
*   **Stripe:** Payment gateway for subscriptions, pay-per-unlock, and expert service transactions. Integrated via Replit connector.
*   **Resend:** Email service for transactional emails (e.g., password resets, notifications). Integrated via Replit connector.
*   **Apify:** Web scraping platform used for daily automated data collection (e.g., from Reddit).
*   **OpenAI/Anthropic (LLMs):** Integrated for AI capabilities like idea generation, validation, opportunity analysis, and expert matching. Specific models like Claude-Haiku and Claude-Sonnet are used.