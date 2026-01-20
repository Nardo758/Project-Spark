# OppGrid - Opportunity Intelligence Platform

## Overview
OppGrid is an AI-powered opportunity intelligence platform designed to help users discover, validate, and act on business opportunities. It provides a structured approach from identifying market frictions to connecting users with experts and resources. The platform aims to be an "AI Startup Factory," offering AI-driven analysis, expert marketplaces, subscription-based content gating, and pay-per-unlock features to foster innovation and entrepreneurial success, with a vision to democratize access to high-quality business intelligence.

## User Preferences
I want iterative development, with a focus on delivering core features quickly and refining them based on feedback. Prioritize modular and reusable code. I prefer clear, concise explanations and direct answers. Ask before making major architectural changes or introducing new external dependencies. Do not make changes to the `replit.nix` file.

## System Architecture
OppGrid utilizes a modern hybrid architecture with a React 18 frontend (Vite, TailwindCSS) on Port 5000 and a Python FastAPI backend (SQLAlchemy ORM) on Port 8000, backed by a Replit PostgreSQL database. Client-side state is managed with Zustand, and routing with React Router v6. The frontend proxies `/api/*` requests to the backend.

**Key Architectural Decisions & Features:**
*   **Monetization & Access Control:** Implements a 3-gate revenue model with multi-tier subscriptions, opportunity slot credits, and pay-per-report features, including white-label and commercial use rights for business tiers.
*   **Team & Access Management:** Supports team creation, role-based access control (owner/admin/member), invitation systems, and API access for business track subscribers with key management and usage tracking.
*   **AI Engine & Analysis:** Integrates with LLMs for idea generation, validation, expert matching, and detailed opportunity analysis. Features an 8-stage "Signal-to-Opportunity" algorithm, automated data pipeline, and AI reliability system with timeouts and structured error handling.
*   **Opportunity Reporting:** Provides 20 AI-generated report templates organized into categories, accessible via a Report Library and Consultant Studio. Includes a "Clone Success" feature for replicating business models with location intelligence and demographic analysis, supporting guest purchases.
*   **Authentication & Security:** Uses Replit's OIDC patterns with database-backed user authentication, including LinkedIn OAuth, password reset functionality, and TOTP-based Two-Factor Authentication (2FA). Webhook security is hardened with production-only secrets and legacy endpoint deprecation.
*   **User Interface & Experience:** Features a professional dark-themed design with a deep dive console, dynamic navigation, and interactive mapping.
*   **Content Moderation:** Implements a quality control workflow requiring admin approval for opportunities to be publicly visible, including side-by-side content comparison and inline editing.
*   **Unified Opportunity Hub & WorkHub (AI Co-Founder):** For paid users, combines research and workspace with a visual journey timeline. The WorkHub is a chat-first conversational AI assistant with a 4-stage workflow (Validate/Research/Plan/Execute), context panels, quick actions, and toolkit panels. Supports "Bring Your Own Key" (BYOK) for Anthropic Claude API keys.
*   **Expert Marketplace & Collaboration:** Features a Leads Marketplace and Network Hub, with an intelligent Expert Recommendation Engine using a weighted scoring algorithm. Facilitates expert interactions with Stripe Connect for payouts, an expert dashboard, and a rating/review system. Expert onboarding supports LinkedIn OAuth pre-population and admin tools for external expert integration (e.g., Upwork).
*   **Data Management:** Ensures complete signal traceability and indefinite data retention. Implements database-backed caching for AI-driven idea validation with a 7-day TTL.
*   **Location Validation:** Centralized `location_utils.py` module provides state bounding box validation to detect and correct out-of-state coordinates from SerpAPI or stored data. Automatic fallback to city/state center coordinates with audit logging ensures map accuracy.
*   **Admin Panel:** Comprehensive tools for managing users, subscriptions, opportunities, leads, and platform statistics.

## External Dependencies
*   **PostgreSQL:** Managed database provided by Replit.
*   **Stripe:** Payment gateway for subscriptions, pay-per-unlock, and expert service transactions (including Stripe Connect).
*   **Resend:** Email service for transactional emails and automation.
*   **Apify:** Web scraping platform for automated data collection.
*   **SerpAPI:** Google Search and Google Maps Reviews API for location-based business intelligence.
*   **OpenAI/Anthropic (LLMs):** Integrated for various AI capabilities.
*   **LinkedIn OAuth:** For professional network authentication.
*   **Census Bureau ACS 5-Year API:** Provides demographic data for opportunity analysis.
*   **Mapbox:** Used for map visualizations.
*   **SBA (Small Business Administration):** Provides curated loan program data and financing course information.