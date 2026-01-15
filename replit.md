# OppGrid - Opportunity Intelligence Platform

## Overview
OppGrid is an AI-powered opportunity intelligence platform designed to help users discover, validate, and act on business opportunities. It provides a structured approach from identifying market frictions to connecting users with experts and resources. The platform aims to be an "AI Startup Factory," offering AI-driven analysis, expert marketplaces, subscription-based content gating, and pay-per-unlock features to foster innovation and entrepreneurial success, with a vision to democratize access to high-quality business intelligence.

## User Preferences
I want iterative development, with a focus on delivering core features quickly and refining them based on feedback. Prioritize modular and reusable code. I prefer clear, concise explanations and direct answers. Ask before making major architectural changes or introducing new external dependencies. Do not make changes to the `replit.nix` file.

## System Architecture
OppGrid utilizes a modern hybrid architecture with a React 18 frontend (Vite, TailwindCSS) on Port 5000 and a Python FastAPI backend (SQLAlchemy ORM) on Port 8000, backed by a Replit PostgreSQL database. Client-side state is managed with Zustand, and routing with React Router v6. The frontend proxies `/api/*` requests to the backend.

**Key Architectural Decisions & Features:**
*   **Monetization & Access Control:** Implements a tiered subscription model (Explorer, Builder, Scaler, Enterprise) with time-decay access control, content gating, and one-time purchases (pay-per-unlock, add-ons).
*   **AI Engine:** Integrates with Large Language Models (LLMs) for idea generation, validation, expert matching, and detailed opportunity analysis, orchestrated by an AI service.
*   **Authentication:** Uses Replit's OIDC patterns with database-backed user authentication, supporting various providers including LinkedIn OAuth.
*   **User Interface:** Features a professional dark-themed design with a deep dive console, dynamic navigation, and interactive mapping (Leaflet.js/Mapbox).
*   **Admin Panel:** Provides comprehensive tools for user, subscription, opportunity, and lead management, along with platform statistics.
*   **Automated Data Pipeline:** A daily scheduler automates data scraping, import, and AI analysis. Includes a webhook-driven data ingestion pipeline for external sources.
*   **Signal-to-Opportunity Algorithm:** An 8-stage processing pipeline converts raw signals into validated business opportunities, categorized into confidence tiers based on pattern matching, clustering, validation scoring, and market size estimation.
*   **Data Lifecycle Management:** Ensures complete signal traceability and indefinite data retention for historical pattern discovery.
*   **Payments & Transactions:** Integrates Stripe for payment processing, subscription management, and pay-per-unlock, including a `SuccessFeeAgreement` infrastructure for expert services.
*   **Opportunity Analysis & Reporting:** AI generates opportunity scores, market size estimates, and business model suggestions. A Consultant Studio offers a three-path validation system, and a report tracking system logs usage.
*   **Design Thinking Report Framework:** Opportunity Detail pages are structured in tiers (FREE, PRO, BUSINESS) based on the Design Thinking process, incorporating AI-generated content across problem detail, research dashboard, and deep dive sections. Reports integrate satellite maps, Census data, and Google Trends via AI-powered generation methods.
*   **Unified Opportunity Hub:** For paid users, combines Research and Workspace capabilities with a visual journey timeline, stage-specific guidance, and automatic workspace creation.
*   **AI Co-Founder:** A conversational AI assistant integrated into the Opportunity Hub provides stage-aware guidance with persistent chat history.
*   **Tool Recommendations Engine:** A curated database of execution tools categorized for various business functions.
*   **Business Formation Guide:** Comprehensive guidance for launching a real business, covering entity types, formation instructions, legal compliance, and financial setup.
*   **Leads Marketplace & Network Hub:** Dedicated platforms for a leads marketplace and connecting users with experts, investors, partners, and lenders.
*   **Expert Recommendation Engine:** An intelligent matching system recommends experts using a weighted scoring algorithm based on category, skills, success metrics, availability, and rating.
*   **Expert Collaboration System:** Facilitates interactions between clients and verified experts through structured engagements, milestones, in-platform messaging, session scheduling, and post-engagement reviews, supporting various engagement types and permission levels.
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