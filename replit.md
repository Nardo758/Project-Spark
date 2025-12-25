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

## Future Features (To Circle Back)
*   **Personal AI Knowledge Base (Brain Dashboard):** Transform the "My AI Co-founder" section (`/brain`) into a personal knowledge repository where users can upload their own data (resume, skills, industry experience, past business plans, preferences). This data would be used to personalize AI Co-Founder responses across all opportunities the user works on. Features to build: document upload/storage, knowledge processing/indexing, AI context injection, user preference settings, daily training questions.