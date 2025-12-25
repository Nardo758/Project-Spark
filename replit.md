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
*   **Monetization & Access Control:** Implements a tiered subscription model (Pro, Business, Enterprise) with time-decay access control for opportunities (HOT, FRESH, VALIDATED, ARCHIVE). Content gating is enforced server-side, with options for one-time purchases (pay-per-unlock, Deep Dive add-on, Fast Pass).
*   **AI Engine:** Integrates with LLMs (e.g., Claude-Haiku, Claude-Sonnet) for AI-powered idea generation, comprehensive idea validation, expert matching, and detailed opportunity analysis (scoring, market size, competition, business models). An AI Orchestrator service routes tasks between different LLMs for specific functionalities.
*   **Authentication:** Uses Replit's OIDC patterns for secure, database-backed user authentication supporting various providers and PKCE flow. Includes LinkedIn OAuth integration for the professional network join flow (experts, investors, partners, lenders) with secure exchange-code pattern. New users are redirected to Profile Onboarding after signup.
*   **User Interface:** Features a professional design with a black/dark stone primary accent. Includes a deep dive console with dark mode, keyboard shortcuts, and export capabilities. Navigation structures are dynamic based on user authentication status.
*   **Admin Panel:** A comprehensive `admin.html` provides tools for user management, subscription control, opportunity moderation, and platform statistics, including lead management and email automation triggers.
*   **Automated Data Pipeline:** A daily scheduler automates data scraping, import, and AI analysis to keep opportunity data fresh. Includes a webhook-driven data ingestion pipeline for external sources like Google Maps, Yelp, Reddit, Twitter, and Nextdoor, with a webhook gateway for validation.
*   **Signal-to-Opportunity Algorithm:** An 8-stage processing pipeline converts raw scraped signals into validated business opportunities:
    - Pattern matching using 700+ keyword patterns across categories (restaurants, apartments, childcare, healthcare, home services)
    - Signal clustering by location and category
    - Validation scoring with 7-criteria weighted scorecard
    - Market size estimation based on population and category penetration
    - Confidence tiers (GOLDMINE, VALIDATED, WEAK_SIGNAL, NOISE)
*   **Data Lifecycle Management:** Complete signal traceability and processing tracking:
    - `scraped_data.processed` flag prevents re-processing of analyzed signals
    - `scraped_data.processing_batch_id` groups signals by processing run
    - `opportunity_signals` link table connects opportunities to their source signals
    - Database indexes for efficient time-based pattern queries
    - All data retained indefinitely for historical pattern discovery
*   **Payments & Transactions:** Integrates Stripe for payment processing, subscription management, and pay-per-unlock features. It includes a `SuccessFeeAgreement` infrastructure with milestone tracking and payout splitting for expert services (70% expert, 20% escrow, 10% platform).
*   **Opportunity Analysis & Reporting:** AI generates opportunity scores, market size estimates, and business model suggestions. A Consultant Studio provides a three-path validation system (Validate Idea, Search Ideas, Identify Location) leveraging AI for analysis and report generation. A report tracking system logs usage and status of generated reports.
*   **Design Thinking Report Framework:** The Opportunity Detail page follows a tiered structure based on the Design Thinking process:
    - **Tier 1: Problem Detail (FREE)** - Empathize + Define: Geographic market selector, quick validation metrics (urgency, competition, target audience, feasibility), pain points with severity badges, problem statement summary
    - **Tier 2: Research Dashboard (PRO - $99/mo)** - Ideate: Tabbed interface (Market Validation, Geographic, Problem Analysis, Sizing, Solutions), demand signals, competitive landscape, solution pathways with business model suggestions
    - **Tier 3: Deep Dive + AI (BUSINESS - $499/mo)** - Prototype + Test: Progress sidebar with section tracking, execution playbook with numbered steps, AI co-pilot chat interface, export/share actions, connect with expert CTA
*   **Interactive Mapping System:** Features a ConsultantMap component with Leaflet.js, displaying business pins, problem heatmaps, and neighborhood polygons, integrated into the Consultant Studio.
*   **Unified Opportunity Hub:** Paid users access `/opportunity/:id/hub` which combines Research and Workspace capabilities in a single interface:
    - Visual journey timeline: Research → Validate → Plan → Build → Launch (auto-updates with workspace status)
    - Research tab: AI validation, market signals, demand indicators, and top expert recommendations
    - Workspace tab: Task management, notes, documents, and AI Co-Founder chat
    - Stage-specific guidance panels that adapt content based on current workspace status
    - Automatic workspace creation when accessing the Hub for the first time
    - Free users continue using Consultant Studio and separate opportunity detail pages
*   **AI Co-Founder:** Conversational AI assistant integrated into the Opportunity Hub that provides stage-aware guidance:
    - **Researching Stage:** Market analysis, competitor mapping, gap identification
    - **Validating Stage:** Customer interview templates, demand signal interpretation, validation evidence
    - **Planning Stage:** Business model design, revenue projections, go-to-market strategy, investor-ready materials
    - **Building Stage:** Execution roadmap, tool recommendations (Replit, Figma, Upwork, etc.), resource allocation
    - **Launched Stage:** Business formation guidance (LLC vs S-Corp), legal compliance, financial setup, growth strategies
    - Chat history persists per workspace for continuity
    - Uses Replit AI Integrations (Claude) - no API key required
*   **Tool Recommendations Engine:** Curated database of execution tools organized by category:
    - Design: Figma, Canva, Framer
    - Development: Replit, Vercel, Supabase, Firebase
    - Talent: Upwork, Toptal, Contra, Fiverr
    - No-Code: Bubble, Webflow, Zapier, Airtable
    - Marketing: Mailchimp, Buffer, SEMrush
    - Project Management: Notion, Linear, Trello
    - Financial: QuickBooks, Wave, Stripe, Mercury
*   **Business Formation Guide:** Comprehensive guidance for launching a real business:
    - Entity type comparison (LLC, S-Corp, Sole Proprietorship)
    - Step-by-step formation instructions
    - EIN registration, business banking, operating agreements
    - Legal compliance, insurance, licenses
    - Tax obligations and bookkeeping setup
*   **Leads Marketplace & Network Hub:** Dedicated pages for a leads marketplace with search/filters and a network hub connecting users with experts, investors, partners, and lenders.
*   **Expert Recommendation Engine:** Intelligent matching system that recommends experts for each opportunity using a weighted scoring algorithm:
    - Category alignment (35%): Matches opportunity category with expert specializations
    - Skill overlap (30%): Compares required skills with expert capabilities
    - Success metrics (20%): Weighs expert success rate and completed projects
    - Availability (10%): Prioritizes currently available experts
    - Rating (5%): Considers average rating and review count
    - API endpoint: GET /opportunities/{id}/experts returns top matched experts with scores and match reasons
    - Integrated into Tier 2 (PRO preview with 3 experts) and Tier 3 (BUSINESS full collaboration with top expert)
*   **Email Automation:** Utilizes an email service for transactional emails, welcome sequences for leads, and status updates, with a template system for professional formatting.

## External Dependencies
*   **PostgreSQL:** Managed database provided by Replit.
*   **Stripe:** Payment gateway for subscriptions, pay-per-unlock, and expert service transactions. Integrated via Replit connector.
*   **Resend:** Email service for transactional emails and automation. Integrated via Replit connector.
*   **Apify:** Web scraping platform used for daily automated data collection. Managed via Command Center Apify tab. Data is imported into the `scraped_data` table which stores business listings and reviews from Google Maps scrapes.
*   **SerpAPI:** Google Search and Google Maps Reviews API integration for location-based business intelligence. Enables searching Google, finding businesses on Google Maps, and fetching place reviews. Managed via Command Center SerpAPI tab. Includes a comprehensive **Google Scraping Framework** with:
    - **Location Catalog:** Database of target locations (cities, metro areas, neighborhoods) with lat/lng coordinates
    - **Keyword Groups:** Organized keyword collections by category (Transportation, Food & Dining, Service Quality, Business Opportunities, Technology)
    - **Scrape Jobs:** Configurable jobs that combine locations + keywords with depth settings and scheduling options
    - **Admin Panel Google Scraping Tab:** Dual-column UI for managing locations and keywords, creating jobs, and viewing results
    - **Database Models:** LocationCatalog, KeywordGroup, GoogleScrapeJob, GoogleMapsBusiness, GoogleSearchCache
*   **OpenAI/Anthropic (LLMs):** Integrated for various AI capabilities, including specific models like Claude-Haiku and Claude-Sonnet.
*   **LinkedIn OAuth:** Integrated for professional network authentication, enabling users to join as experts, investors, partners, or lenders using their LinkedIn credentials.

## Enhancement Roadmap

A comprehensive roadmap has been created at `docs/ENHANCEMENT_ROADMAP.md` with 6 phases covering:

1. **Phase 1: Complete User Flow** (Weeks 1-2) - Collections, Tags, Notes system
2. **Phase 2: Opportunity Lifecycle** (Weeks 3-4) - 8 lifecycle states with transitions
3. **Phase 3: Persistent AI Copilot** (Weeks 5-6) - Cross-page AI assistant
4. **Phase 4: Expert Collaboration** (Weeks 7-9) - Full expert matching and engagement
5. **Phase 5: Launch Guidance** (Weeks 10-12) - Business formation wizard
6. **Phase 6: Enhanced Tools** (Weeks 13-14) - 200+ tool database

Total estimated timeline: 14 weeks (3.5 months)

## Recent Changes (December 25, 2025)

- **Phase 3 Enhancement Complete:** Persistent AI Copilot
  - GlobalChatMessage and CopilotSuggestion database models for cross-page conversation persistence
  - Copilot API router with chat, history, suggestions, and smart tagging endpoints
  - AICopilotPanel component: collapsible floating panel visible on all pages
  - Page context awareness: copilot knows current page (feed, saved, opportunity_detail, hub, etc.)
  - Opportunity context: when viewing an opportunity, copilot has access to its details
  - Lifecycle state awareness: copilot knows user's progress with saved opportunities
  - AI-powered tag suggestions endpoint for opportunities
  - Proactive suggestions display based on current context
- **Phase 2 Enhancement Complete:** Opportunity Lifecycle States
  - LifecycleState enum with 8 states: discovered, saved, analyzing, planning, executing, launched, paused, archived
  - lifecycle_state, state_changed_at, paused_reason, archived_reason columns on watchlist_items
  - Lifecycle API endpoints: GET /states, GET /summary, GET /by-state, POST /transition
  - LifecycleTimeline React component with compact and full views
  - Visual journey timeline showing progression through stages
  - Workspace-to-lifecycle sync: workspace status changes automatically update lifecycle state
  - Journey Stages summary panel in Saved page sidebar
  - PAUSED and ARCHIVED states with reason input dialogs
- **Phase 1 Enhancement Complete:** Collections, Tags, and Notes system
  - UserCollection model for organizing saved opportunities into folders
  - UserTag model with custom colors for labeling opportunities
  - OpportunityNote model for adding notes to opportunities
  - Enhanced Saved page UI with collections sidebar, tags panel, and note editor
  - API endpoints for CRUD operations on collections, tags, and notes
  - Watchlist filtering by collection
- Added AI Co-Founder chat feature with stage-specific guidance
- Implemented tool recommendations engine (50+ tools)
- Added business formation guide (LLC, S-Corp, Sole Proprietorship)
- Created stage-specific guidance panels in workspace sidebar
- Added "Open Hub" button on opportunity detail page for paid users
- Created comprehensive enhancement roadmap documentation