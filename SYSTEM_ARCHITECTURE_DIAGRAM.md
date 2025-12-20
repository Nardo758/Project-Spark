# Friction (OppGrid) - Complete System Architecture & Features

> **Last Updated:** 2025-12-20
> **Version:** 2.0
> **Project:** Friction - Problem Discovery Search Engine

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Complete Architecture Diagram](#complete-architecture-diagram)
3. [Technology Stack](#technology-stack)
4. [Frontend Architecture](#frontend-architecture)
5. [Backend Architecture](#backend-architecture)
6. [Database Schema](#database-schema)
7. [Feature Mapping](#feature-mapping)
8. [Data Flow Diagrams](#data-flow-diagrams)
9. [Security Architecture](#security-architecture)
10. [Deployment Architecture](#deployment-architecture)

---

## 🎯 System Overview

**Friction** is a comprehensive problem discovery and validation platform that helps founders, researchers, and innovators discover real-world problems, validate market opportunities, and connect with experts. The platform combines AI-powered analysis with human validation to surface high-potential opportunities.

### Key Capabilities

- 🔍 **Discovery Engine**: Browse and search validated real-world problems
- 🤖 **AI Co-founder**: Personal AI assistant for opportunity analysis
- 💡 **Idea Engine**: AI-powered idea validation and market analysis
- 📊 **Analytics Dashboard**: Deep-dive analytics and feasibility scoring
- 🌐 **Expert Marketplace**: Connect with domain experts
- 💳 **Payment Integration**: Stripe-powered subscriptions and one-time unlocks
- 🔐 **Secure Authentication**: Multi-provider OAuth, magic links, 2FA

---

## 🏗️ Complete Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer - User Interface"
        Browser[User Browser]

        subgraph "Modern React Frontend (Port 5173)"
            ReactApp[React + TypeScript<br/>Vite Dev Server]
            ReactRouter[React Router]
            ReactPages[Pages:<br/>Home, Discover, Brain,<br/>Dashboard, Pricing, etc.]
            ReactComponents[Shared Components:<br/>Layout, Navbar, etc.]
            ReactStores[Zustand Stores:<br/>authStore, brainStore]
            ReactServices[API Services:<br/>brainApi, deepseekApi]
        end

        subgraph "Legacy Frontend (Port 5000)"
            StaticPages[Static HTML Pages:<br/>index.html, signin.html,<br/>opportunity.html, etc.]
            VanillaJS[Vanilla JavaScript:<br/>app.js, api.js, auth.js]
            StaticCSS[CSS Styles]
        end
    end

    subgraph "Network Layer"
        HTTPS[HTTPS/TLS]
        CORS[CORS Middleware]
        RateLimit[Rate Limiter]
    end

    subgraph "Application Server Layer (Port 8000)"
        FastAPI[FastAPI Application]

        subgraph "Middleware Stack"
            SecurityMw[Security Headers]
            RateLimitMw[Rate Limiting]
            CORSMw[CORS Handler]
            AuthMw[JWT Auth Middleware]
        end

        subgraph "API Router Layer - 30+ Routers"
            AuthRouter[auth.py<br/>Login, Register, Verify]
            OAuthRouter[oauth.py<br/>Google, GitHub]
            MagicLinkRouter[magic_link.py<br/>Passwordless Auth]
            TwoFactorRouter[two_factor.py<br/>TOTP 2FA]

            OppRouter[opportunities.py<br/>CRUD Operations]
            ValidationRouter[validations.py<br/>User Validations]
            CommentRouter[comments.py<br/>Comments & Discussion]
            WatchlistRouter[watchlist.py<br/>Save Opportunities]
            FollowRouter[follows.py<br/>Follow Users/Categories]

            BrainRouter[brains.py<br/>AI Co-founder State]
            DeepSeekRouter[deepseek.py<br/>AI Analysis & Matching]
            IdeaEngineRouter[idea_engine.py<br/>Idea Validation]
            IdeaValRouter[idea_validations.py<br/>Validation Records]
            AIEngineRouter[ai_engine.py<br/>AI Processing]
            AIAnalysisRouter[ai_analysis.py<br/>Analysis Service]
            AIChatRouter[ai_chat.py<br/>Chat Interface]

            SubscriptionRouter[subscriptions.py<br/>Tier Management]
            PaymentRouter[payments.py<br/>Payment Processing]
            StripeWebhookRouter[stripe_webhook.py<br/>Stripe Events]

            ExpertRouter[experts.py<br/>Expert Profiles]
            ProfileRouter[profiles.py<br/>User Profiles]
            AgreementRouter[agreements.py<br/>Service Agreements]

            AnalyticsRouter[analytics.py<br/>Statistics & Insights]
            AdminRouter[admin.py<br/>Admin Panel]
            ModerationRouter[moderation.py<br/>Content Moderation]
            NotificationRouter[notifications.py<br/>User Notifications]
            WebSocketRouter[websocket_router.py<br/>Real-time Updates]

            OtherRouters[... + 10 more routers]
        end

        subgraph "Service Layer - Business Logic"
            StripeService[stripe_service.py<br/>Payment Logic]
            EmailService[email_service.py<br/>Email Notifications]
            UsageService[usage_service.py<br/>Usage Tracking]
            AIService[ai_service.py<br/>AI Processing]
            DeepSeekService[deepseek_service.py<br/>DeepSeek Integration]
            ModerationService[moderation_service.py<br/>Content Filtering]
            AnalyticsService[analytics_service.py<br/>Data Analysis]
            NotificationService[notification_service.py<br/>Push Notifications]
            WebSocketBroadcaster[websocket_broadcaster.py<br/>Real-time Broadcasting]
        end

        subgraph "Data Access Layer - ORM Models"
            UserModel[User<br/>Authentication & Profile]
            OppModel[Opportunity<br/>Problems & Needs]
            ValidationModel[Validation<br/>User Votes]
            CommentModel[Comment<br/>Discussions]
            WatchlistModel[Watchlist<br/>Saved Items]
            FollowModel[Follow<br/>User/Category Following]

            BrainModel[Brain<br/>AI Co-founder State]
            IdeaValidationModel[IdeaValidation<br/>AI Validation Results]

            SubscriptionModel[Subscription<br/>User Tiers]
            TransactionModel[Transaction<br/>Payment History]
            StripeEventModel[StripeEvent<br/>Webhook Events]

            ExpertModel[Expert<br/>Expert Profiles]
            UserProfileModel[UserProfile<br/>Extended Profiles]
            AgreementModel[Agreement<br/>Service Contracts]
            BookingModel[Booking<br/>Expert Sessions]

            NotificationModel[Notification<br/>User Alerts]
            AuditLogModel[AuditLog<br/>System Audit Trail]
            TrackingModel[TrackingEvent<br/>Analytics Events]
            JobRunModel[JobRun<br/>Background Jobs]
            PartnerModel[Partner<br/>Partner Outreach]

            OtherModels[... + more models]
        end
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database<br/>Replit Managed<br/>SQLAlchemy ORM)]
        Redis[(Redis Cache<br/>Optional<br/>Session & Rate Limiting)]
    end

    subgraph "External Services"
        subgraph "Payment Gateway"
            StripeAPI[Stripe API<br/>Subscriptions & Payments]
            StripeCheckout[Stripe Checkout<br/>Payment UI]
            StripePortal[Stripe Billing Portal<br/>Self-Service]
        end

        subgraph "OAuth Providers"
            GoogleOAuth[Google OAuth 2.0]
            GitHubOAuth[GitHub OAuth]
            ReplitAuth[Replit Auth]
        end

        subgraph "Email & Communication"
            ResendAPI[Resend Email API<br/>Transactional Emails]
        end

        subgraph "AI Services"
            DeepSeekAPI[DeepSeek AI<br/>Analysis & Matching]
            OpenAIAPI[OpenAI API<br/>ChatGPT Integration]
        end

        subgraph "Analytics & Monitoring"
            SentryMonitoring[Sentry<br/>Error Tracking]
            AnalyticsService[Analytics Platform<br/>Usage Tracking]
        end
    end

    %% Client to Frontend Connections
    Browser --> ReactApp
    Browser --> StaticPages

    ReactApp --> ReactRouter
    ReactRouter --> ReactPages
    ReactPages --> ReactComponents
    ReactPages --> ReactStores
    ReactPages --> ReactServices

    StaticPages --> VanillaJS

    %% Frontend to Backend Connections
    ReactServices -->|HTTPS API Calls| HTTPS
    VanillaJS -->|HTTPS API Calls| HTTPS

    %% Network Layer
    HTTPS --> CORS
    CORS --> RateLimit
    RateLimit --> FastAPI

    %% Middleware Processing
    FastAPI --> SecurityMw
    SecurityMw --> RateLimitMw
    RateLimitMw --> CORSMw
    CORSMw --> AuthMw

    %% Router Connections
    AuthMw --> AuthRouter
    AuthMw --> OAuthRouter
    AuthMw --> MagicLinkRouter
    AuthMw --> TwoFactorRouter

    AuthMw --> OppRouter
    AuthMw --> ValidationRouter
    AuthMw --> CommentRouter
    AuthMw --> WatchlistRouter
    AuthMw --> FollowRouter

    AuthMw --> BrainRouter
    AuthMw --> DeepSeekRouter
    AuthMw --> IdeaEngineRouter
    AuthMw --> IdeaValRouter
    AuthMw --> AIEngineRouter

    AuthMw --> SubscriptionRouter
    AuthMw --> PaymentRouter
    AuthMw --> StripeWebhookRouter

    AuthMw --> ExpertRouter
    AuthMw --> ProfileRouter

    AuthMw --> AnalyticsRouter
    AuthMw --> AdminRouter
    AuthMw --> NotificationRouter
    AuthMw --> WebSocketRouter

    %% Router to Service Connections
    AuthRouter --> EmailService
    OppRouter --> AIService
    OppRouter --> ModerationService

    BrainRouter --> DeepSeekService
    DeepSeekRouter --> DeepSeekService
    IdeaEngineRouter --> AIService

    SubscriptionRouter --> StripeService
    PaymentRouter --> StripeService
    StripeWebhookRouter --> StripeService

    NotificationRouter --> NotificationService
    WebSocketRouter --> WebSocketBroadcaster

    AnalyticsRouter --> AnalyticsService

    %% Service to Model Connections
    StripeService --> SubscriptionModel
    StripeService --> TransactionModel
    StripeService --> StripeEventModel

    AIService --> IdeaValidationModel
    DeepSeekService --> BrainModel

    EmailService --> UserModel
    NotificationService --> NotificationModel
    AnalyticsService --> TrackingModel

    %% Model to Database Connections
    UserModel -->|SQLAlchemy| PostgreSQL
    OppModel -->|SQLAlchemy| PostgreSQL
    ValidationModel -->|SQLAlchemy| PostgreSQL
    CommentModel -->|SQLAlchemy| PostgreSQL
    WatchlistModel -->|SQLAlchemy| PostgreSQL
    FollowModel -->|SQLAlchemy| PostgreSQL

    BrainModel -->|SQLAlchemy| PostgreSQL
    IdeaValidationModel -->|SQLAlchemy| PostgreSQL

    SubscriptionModel -->|SQLAlchemy| PostgreSQL
    TransactionModel -->|SQLAlchemy| PostgreSQL
    StripeEventModel -->|SQLAlchemy| PostgreSQL

    ExpertModel -->|SQLAlchemy| PostgreSQL
    UserProfileModel -->|SQLAlchemy| PostgreSQL
    AgreementModel -->|SQLAlchemy| PostgreSQL
    BookingModel -->|SQLAlchemy| PostgreSQL

    NotificationModel -->|SQLAlchemy| PostgreSQL
    AuditLogModel -->|SQLAlchemy| PostgreSQL
    TrackingModel -->|SQLAlchemy| PostgreSQL
    JobRunModel -->|SQLAlchemy| PostgreSQL
    PartnerModel -->|SQLAlchemy| PostgreSQL
    OtherModels -->|SQLAlchemy| PostgreSQL

    %% Cache Connections
    AuthMw -.->|Session Cache| Redis
    RateLimitMw -.->|Rate Limits| Redis

    %% External Service Connections
    StripeService -->|API Calls| StripeAPI
    StripeService -->|Create Sessions| StripeCheckout
    StripeService -->|Portal Sessions| StripePortal
    StripeAPI -->|Webhooks| StripeWebhookRouter

    OAuthRouter -->|OAuth Flow| GoogleOAuth
    OAuthRouter -->|OAuth Flow| GitHubOAuth
    OAuthRouter -->|OAuth Flow| ReplitAuth

    EmailService -->|Send Emails| ResendAPI

    DeepSeekService -->|AI Analysis| DeepSeekAPI
    AIService -->|Chat Completion| OpenAIAPI

    FastAPI -.->|Error Tracking| SentryMonitoring
    AnalyticsService -.->|Events| AnalyticsService

    %% Styling
    style Browser fill:#e1f5ff,stroke:#0277bd,stroke-width:2px
    style ReactApp fill:#61dafb,stroke:#00d8ff,stroke-width:2px
    style StaticPages fill:#f0f0f0,stroke:#666,stroke-width:2px
    style FastAPI fill:#009688,stroke:#00695c,stroke-width:3px
    style PostgreSQL fill:#336791,stroke:#1a4d7a,stroke-width:3px
    style Redis fill:#dc382d,stroke:#a32820,stroke-width:2px
    style StripeAPI fill:#635bff,stroke:#4338ca,stroke-width:2px
    style DeepSeekAPI fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px
    style GoogleOAuth fill:#4285f4,stroke:#1967d2,stroke-width:2px
    style ResendAPI fill:#6366f1,stroke:#4338ca,stroke-width:2px
```

---

## 🛠️ Technology Stack

### Frontend Technologies

| Layer | Technology | Purpose | Location |
|-------|-----------|---------|----------|
| **Modern UI Framework** | React 18+ | Component-based UI | `frontend/src/` |
| **Language** | TypeScript 5+ | Type-safe JavaScript | `frontend/src/**/*.tsx` |
| **Build Tool** | Vite 5+ | Fast dev server & bundler | `frontend/vite.config.ts` |
| **Routing** | React Router v6 | Client-side routing | `frontend/src/App.tsx` |
| **State Management** | Zustand | Lightweight state store | `frontend/src/stores/` |
| **Styling** | Tailwind CSS 3+ | Utility-first CSS | `frontend/tailwind.config.js` |
| **HTTP Client** | Fetch API | API communication | `frontend/src/services/` |
| **Legacy Frontend** | Vanilla JavaScript | Static pages | `js/app.js`, `js/api.js` |
| **Legacy Styling** | Custom CSS | Component styles | `css/styles.css` |

### Backend Technologies

| Layer | Technology | Purpose | Location |
|-------|-----------|---------|----------|
| **Framework** | FastAPI 0.109+ | High-performance async API | `backend/app/main.py` |
| **Language** | Python 3.11+ | Backend logic | `backend/app/**/*.py` |
| **ASGI Server** | Uvicorn | Production ASGI server | `backend/` |
| **ORM** | SQLAlchemy 2.0+ | Database abstraction | `backend/app/models/` |
| **Migrations** | Alembic 1.13+ | Database versioning | `backend/alembic/` |
| **Authentication** | JWT (python-jose) | Token-based auth | `backend/app/core/security.py` |
| **OAuth** | Authlib | Social login | `backend/app/routers/oauth.py` |
| **Password Hashing** | bcrypt (passlib) | Secure passwords | `backend/app/core/security.py` |
| **Data Validation** | Pydantic 2.0+ | Request/response validation | `backend/app/schemas/` |

### Database & Caching

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Primary Database** | PostgreSQL 14+ | Relational data storage |
| **ORM** | SQLAlchemy 2.0 | Database abstraction layer |
| **Connection Pool** | SQLAlchemy Pool | Connection management |
| **Migrations** | Alembic | Schema versioning |
| **Cache (Optional)** | Redis 7+ | Session & rate limit cache |

### External Services

| Service | Purpose | Integration |
|---------|---------|-------------|
| **Stripe** | Payments & subscriptions | `backend/app/services/stripe_service.py` |
| **Resend** | Transactional emails | `backend/app/services/email_service.py` |
| **DeepSeek AI** | AI analysis & matching | `backend/app/services/deepseek_service.py` |
| **OpenAI** | ChatGPT integration | `backend/app/routers/ai_chat.py` |
| **Google OAuth** | Social login | `backend/app/core/oauth_config.py` |
| **GitHub OAuth** | Social login | `backend/app/core/oauth_config.py` |
| **Replit Auth** | Platform SSO | `backend/app/routers/replit_auth.py` |
| **Sentry** | Error monitoring | `backend/app/main.py` |

### DevOps & Deployment

| Tool | Purpose | Location |
|------|---------|----------|
| **Platform** | Replit | Hosting & deployment |
| **Server** | Dual-thread server | `server.py` |
| **Environment** | .env files | `.env`, `backend/.env` |
| **Version Control** | Git & GitHub | `.git/` |
| **Package Manager (Python)** | pip | `backend/requirements.txt` |
| **Package Manager (JS)** | npm | `frontend/package.json` |

---

## 🎨 Frontend Architecture

### React Frontend Structure

```mermaid
graph TB
    subgraph "React Application (frontend/)"
        Entry[index.html + main.tsx]

        subgraph "Root Component"
            App[App.tsx<br/>Router + Layout]
        end

        subgraph "Layout Components"
            Layout[components/Layout.tsx<br/>Auth Bootstrap]
            Navbar[components/Navbar.tsx<br/>Navigation + Brain Status]
            Footer[components/Footer.tsx]
        end

        subgraph "Page Components"
            Home[pages/Home.tsx]
            Discover[pages/Discover.tsx]
            OppDetail[pages/OpportunityDetail.tsx]

            Brain[pages/brain/BrainDashboard.tsx]
            IdeaEngine[pages/IdeaEngine.tsx]
            AIMatch[pages/AIMatch.tsx]
            AIRoadmap[pages/AIRoadmap.tsx]

            Dashboard[pages/Dashboard.tsx]
            Saved[pages/Saved.tsx]

            Pricing[pages/Pricing.tsx]
            Marketplace[pages/ExpertMarketplace.tsx]

            Login[pages/Login.tsx]
            Signup[pages/Signup.tsx]
            AuthCallback[pages/AuthCallback.tsx]
            MagicCallback[pages/MagicLinkCallback.tsx]

            About[pages/About.tsx]
            Blog[pages/Blog.tsx]
            Contact[pages/Contact.tsx]
            Terms[pages/Terms.tsx]
            Privacy[pages/Privacy.tsx]

            OtherPages[... + 10 more pages]
        end

        subgraph "State Management (Zustand)"
            AuthStore[stores/authStore.ts<br/>User Session & JWT]
            BrainStore[stores/brainStore.ts<br/>AI Co-founder State]
        end

        subgraph "API Services"
            BrainAPI[services/brainApi.ts<br/>/brains/* client]
            DeepSeekAPI[services/deepseekApi.ts<br/>/deepseek/* client]
            OppAPI[services/opportunityApi.ts<br/>/opportunities/* client]
        end

        subgraph "Utilities"
            Types[types/<br/>TypeScript Definitions]
            Utils[utils/<br/>Helper Functions]
            Config[config/<br/>Environment Config]
        end
    end

    Entry --> App
    App --> Layout
    Layout --> Navbar
    Layout --> Home
    Layout --> Discover
    Layout --> Brain
    Layout --> Dashboard

    Navbar --> AuthStore
    Navbar --> BrainStore

    Discover --> OppDetail
    Discover --> OppAPI

    Brain --> BrainAPI
    Brain --> BrainStore

    IdeaEngine --> DeepSeekAPI
    AIMatch --> DeepSeekAPI

    Login --> AuthStore
    Signup --> AuthStore
    AuthCallback --> AuthStore
    MagicCallback --> AuthStore

    Dashboard --> AuthStore
    Saved --> AuthStore

    style App fill:#61dafb,stroke:#00d8ff
    style AuthStore fill:#ffd700,stroke:#ff8c00
    style BrainStore fill:#ffd700,stroke:#ff8c00
```

### Legacy Frontend Structure

```mermaid
graph LR
    subgraph "Static HTML Pages (Root)"
        Index[index.html<br/>Main App]
        SignIn[signin.html]
        SignUp[signup.html]
        Opportunity[opportunity.html]
        Account[account.html]
        Pricing2[pricing.html]
        Admin[admin.html]
        Submit[submit.html]
        OtherHTML[... + 20 more pages]
    end

    subgraph "JavaScript Layer (js/)"
        AppJS[app.js<br/>Application Logic<br/>Tab Navigation]
        ApiJS[api.js<br/>OppGridAPI Class<br/>HTTP Client]
        AuthJS[auth.js<br/>JWT Storage<br/>Auth Checks]
        ConfigJS[config.js<br/>API Base URL<br/>Environment]
    end

    subgraph "Styling (css/)"
        Styles[styles.css<br/>Component Styles]
    end

    Index --> AppJS
    SignIn --> AppJS
    Opportunity --> AppJS

    AppJS --> ApiJS
    AppJS --> AuthJS

    ApiJS --> ConfigJS
    AuthJS --> ConfigJS

    style Index fill:#f0f0f0
    style ApiJS fill:#90caf9
    style AuthJS fill:#90caf9
```

### Frontend Features by Route

| Route | Component | Features | Auth Required |
|-------|-----------|----------|---------------|
| `/` | Home.tsx | Landing page, hero, CTAs | ❌ No |
| `/discover` | Discover.tsx | Browse opportunities, filters | ❌ No |
| `/opportunity/:id` | OpportunityDetail.tsx | View details, validate, comment | Partial |
| `/brain` | BrainDashboard.tsx | AI co-founder interface | ✅ Yes |
| `/idea-engine` | IdeaEngine.tsx | Submit ideas for validation | ✅ Yes |
| `/ai-match` | AIMatch.tsx | AI opportunity matching | ✅ Yes |
| `/dashboard` | Dashboard.tsx | User analytics, saved items | ✅ Yes |
| `/saved` | Saved.tsx | Watchlist, bookmarks | ✅ Yes |
| `/pricing` | Pricing.tsx | Subscription plans, checkout | ❌ No |
| `/experts` | ExpertMarketplace.tsx | Browse experts, book sessions | ❌ No |
| `/login` | Login.tsx | Email/OAuth login, magic link | ❌ No |
| `/signup` | Signup.tsx | User registration | ❌ No |
| `/auth/callback` | AuthCallback.tsx | OAuth callback handler | ❌ No |
| `/auth/magic` | MagicLinkCallback.tsx | Magic link handler | ❌ No |

---

## ⚙️ Backend Architecture

### API Router Organization

```mermaid
graph TB
    subgraph "FastAPI Application"
        Main[main.py<br/>App Entry Point]

        subgraph "Authentication & Users (6 routers)"
            Auth[auth.py<br/>Login, Register, Verify Email]
            OAuth[oauth.py<br/>Google, GitHub, Replit]
            MagicLink[magic_link.py<br/>Passwordless Auth]
            TwoFactor[two_factor.py<br/>TOTP 2FA]
            Users[users.py<br/>User Management]
            Profiles[profiles.py<br/>Extended Profiles]
        end

        subgraph "Core Opportunities (6 routers)"
            Opportunities[opportunities.py<br/>CRUD, Search, Filters]
            Validations[validations.py<br/>Vote, Unvote]
            Comments[comments.py<br/>Discussion Threads]
            Watchlist[watchlist.py<br/>Save, Bookmark]
            Follows[follows.py<br/>Follow Users/Categories]
            Social[social.py<br/>Social Features]
        end

        subgraph "AI Features (7 routers)"
            Brains[brains.py<br/>AI Co-founder State Management]
            DeepSeek[deepseek.py<br/>AI Analysis & Scoring]
            IdeaEngine[idea_engine.py<br/>Idea Submission]
            IdeaVal[idea_validations.py<br/>Validation Results]
            AIEngine[ai_engine.py<br/>AI Processing Pipeline]
            AIAnalysis[ai_analysis.py<br/>Detailed Analysis]
            AIChat[ai_chat.py<br/>Chat Interface]
        end

        subgraph "Payments (3 routers)"
            Subscriptions[subscriptions.py<br/>Tier Management, Checkout]
            Payments[payments.py<br/>One-time Payments]
            StripeWebhook[stripe_webhook.py<br/>Webhook Handler]
        end

        subgraph "Marketplace (3 routers)"
            Experts[experts.py<br/>Expert Profiles & Search]
            Agreements[agreements.py<br/>Service Contracts]
            Bookings[bookings.py<br/>Session Booking]
        end

        subgraph "Platform Features (5 routers)"
            Analytics[analytics.py<br/>Statistics & Insights]
            Notifications[notifications.py<br/>User Alerts]
            Admin[admin.py<br/>Admin Operations]
            Moderation[moderation.py<br/>Content Moderation]
            WebSocket[websocket_router.py<br/>Real-time Updates]
        end

        subgraph "Utility Routers (3 routers)"
            Contact[contact.py<br/>Contact Forms]
            Webhook[webhook.py<br/>Generic Webhooks]
            Scraper[scraper.py<br/>Data Collection]
        end
    end

    Main --> Auth
    Main --> OAuth
    Main --> MagicLink
    Main --> TwoFactor
    Main --> Users
    Main --> Profiles

    Main --> Opportunities
    Main --> Validations
    Main --> Comments
    Main --> Watchlist
    Main --> Follows
    Main --> Social

    Main --> Brains
    Main --> DeepSeek
    Main --> IdeaEngine
    Main --> IdeaVal
    Main --> AIEngine
    Main --> AIAnalysis
    Main --> AIChat

    Main --> Subscriptions
    Main --> Payments
    Main --> StripeWebhook

    Main --> Experts
    Main --> Agreements

    Main --> Analytics
    Main --> Notifications
    Main --> Admin
    Main --> Moderation
    Main --> WebSocket

    Main --> Contact
    Main --> Webhook
    Main --> Scraper

    style Main fill:#009688,stroke:#00695c,stroke-width:3px
    style Auth fill:#4caf50,stroke:#388e3c
    style Opportunities fill:#2196f3,stroke:#1976d2
    style Brains fill:#ff6b6b,stroke:#c92a2a
    style Subscriptions fill:#635bff,stroke:#4338ca
```

### Service Layer Architecture

```mermaid
graph LR
    subgraph "Routers (HTTP Endpoints)"
        R1[Opportunities]
        R2[Subscriptions]
        R3[Brains]
        R4[Notifications]
        R5[Analytics]
    end

    subgraph "Service Layer (Business Logic)"
        S1[stripe_service.py<br/>Payment Processing]
        S2[email_service.py<br/>Email Delivery]
        S3[usage_service.py<br/>Usage Tracking]
        S4[deepseek_service.py<br/>AI Integration]
        S5[notification_service.py<br/>Alert Management]
        S6[analytics_service.py<br/>Data Aggregation]
        S7[moderation_service.py<br/>Content Filtering]
        S8[websocket_broadcaster.py<br/>Real-time Push]
    end

    subgraph "External APIs"
        E1[Stripe API]
        E2[Resend Email]
        E3[DeepSeek AI]
        E4[OpenAI]
    end

    R1 --> S4
    R1 --> S7
    R2 --> S1
    R2 --> S3
    R3 --> S4
    R4 --> S5
    R4 --> S8
    R5 --> S6

    S1 --> E1
    S2 --> E2
    S4 --> E3
    S4 --> E4

    style S1 fill:#ffd700
    style S4 fill:#ff6b6b
    style S8 fill:#9c27b0
```

---

## 🗄️ Database Schema

### Core Entity Relationships

```mermaid
erDiagram
    USER ||--o{ OPPORTUNITY : creates
    USER ||--o{ VALIDATION : makes
    USER ||--o{ COMMENT : posts
    USER ||--o{ WATCHLIST : saves
    USER ||--o{ FOLLOW : follows
    USER ||--|| SUBSCRIPTION : has
    USER ||--o{ BRAIN : owns
    USER ||--|| USER_PROFILE : has
    USER ||--o{ IDEA_VALIDATION : requests
    USER ||--o{ NOTIFICATION : receives
    USER ||--o{ TRANSACTION : makes
    USER ||--o{ AUDIT_LOG : generates
    USER ||--o{ TRACKING_EVENT : triggers

    OPPORTUNITY ||--o{ VALIDATION : receives
    OPPORTUNITY ||--o{ COMMENT : has
    OPPORTUNITY ||--o{ WATCHLIST : in
    OPPORTUNITY ||--o{ SHARE : shared
    OPPORTUNITY ||--o{ REPORT : flagged_in

    BRAIN ||--o{ BRAIN_OPPORTUNITY : tracks
    BRAIN ||--o{ BRAIN_TIMELINE : has

    EXPERT ||--o{ BOOKING : offers
    EXPERT ||--o{ AGREEMENT : provides
    EXPERT ||--|| USER : is

    SUBSCRIPTION ||--o{ TRANSACTION : has
    SUBSCRIPTION ||--o{ STRIPE_EVENT : receives

    IDEA_VALIDATION ||--|| OPPORTUNITY : analyzes

    USER {
        int id PK
        string email UK
        string hashed_password
        string name
        string oauth_provider
        string oauth_id UK
        int impact_points
        boolean is_verified
        boolean is_admin
        string otp_secret
        boolean otp_enabled
        timestamp created_at
        timestamp updated_at
    }

    OPPORTUNITY {
        int id PK
        string title
        text description
        string category
        int severity
        int validation_count
        float feasibility_score
        string geographic_scope
        string completion_status
        int author_id FK
        boolean is_anonymous
        int duplicate_of FK
        boolean ai_analyzed
        float ai_opportunity_score
        timestamp created_at
    }

    VALIDATION {
        int id PK
        int user_id FK
        int opportunity_id FK
        timestamp created_at
        UK user_id_opportunity_id
    }

    COMMENT {
        int id PK
        int user_id FK
        int opportunity_id FK
        text content
        int likes
        int parent_id FK
        timestamp created_at
    }

    WATCHLIST {
        int id PK
        int user_id FK
        int opportunity_id FK
        timestamp added_at
        UK user_id_opportunity_id
    }

    FOLLOW {
        int id PK
        int follower_id FK
        int following_id FK
        string follow_type
        timestamp created_at
        UK follower_following
    }

    SUBSCRIPTION {
        int id PK
        int user_id FK_UK
        string tier
        string status
        string stripe_customer_id
        string stripe_subscription_id
        string stripe_price_id
        timestamp current_period_start
        timestamp current_period_end
        boolean cancel_at_period_end
        timestamp created_at
    }

    BRAIN {
        int id PK
        int user_id FK
        string name
        string status
        jsonb config
        jsonb state
        timestamp created_at
        timestamp updated_at
    }

    BRAIN_OPPORTUNITY {
        int id PK
        int brain_id FK
        int opportunity_id FK
        float match_score
        text reasoning
        timestamp added_at
    }

    USER_PROFILE {
        int id PK
        int user_id FK_UK
        string bio
        string location
        string website
        string linkedin
        string twitter
        string github
        jsonb skills
        timestamp created_at
    }

    EXPERT {
        int id PK
        int user_id FK_UK
        string expertise_area
        int hourly_rate
        boolean verified
        float rating
        int total_sessions
        timestamp created_at
    }

    BOOKING {
        int id PK
        int expert_id FK
        int user_id FK
        timestamp session_time
        int duration_minutes
        string status
        int amount_paid
        timestamp created_at
    }

    AGREEMENT {
        int id PK
        int expert_id FK
        int user_id FK
        text terms
        string status
        timestamp signed_at
    }

    IDEA_VALIDATION {
        int id PK
        int user_id FK
        int opportunity_id FK
        text analysis
        float score
        jsonb metrics
        int tokens_used
        int cost_cents
        timestamp created_at
    }

    TRANSACTION {
        int id PK
        int user_id FK
        int subscription_id FK
        int amount
        string currency
        string status
        string stripe_payment_intent_id
        timestamp created_at
    }

    STRIPE_EVENT {
        int id PK
        string event_id UK
        string event_type
        jsonb data
        boolean processed
        timestamp created_at
    }

    NOTIFICATION {
        int id PK
        int user_id FK
        string type
        string title
        text message
        boolean read
        jsonb metadata
        timestamp created_at
    }

    AUDIT_LOG {
        int id PK
        int user_id FK
        string action
        string entity_type
        int entity_id
        jsonb changes
        string ip_address
        timestamp created_at
    }

    TRACKING_EVENT {
        int id PK
        int user_id FK
        string event_type
        string page
        jsonb properties
        timestamp created_at
    }
```

---

## 🎯 Feature Mapping

### Complete Feature-to-Code Matrix

| Feature Area | Frontend Code | Backend Code | Database Tables |
|--------------|---------------|--------------|-----------------|
| **🔐 Authentication & Authorization** |
| Email/Password Login | `pages/Login.tsx`<br/>`stores/authStore.ts` | `routers/auth.py`<br/>`core/security.py` | `users` |
| Social OAuth (Google/GitHub) | `pages/AuthCallback.tsx`<br/>`stores/authStore.ts` | `routers/oauth.py`<br/>`core/oauth_config.py` | `users`<br/>`oauth_accounts` |
| Magic Link Login | `pages/MagicLinkCallback.tsx` | `routers/magic_link.py` | `users`<br/>`magic_link_tokens` |
| 2FA/TOTP | UI in account settings | `routers/two_factor.py` | `users.otp_secret` |
| Replit SSO | Auto-redirect | `routers/replit_auth.py` | `users` |
| **🔍 Opportunity Discovery** |
| Browse Opportunities | `pages/Discover.tsx` | `routers/opportunities.py` | `opportunities` |
| Search & Filters | `pages/Discover.tsx` | `routers/opportunities.py` | `opportunities` |
| Opportunity Detail | `pages/OpportunityDetail.tsx` | `routers/opportunities.py` | `opportunities`<br/>`validations`<br/>`comments` |
| Category Browse | `pages/Discover.tsx` | `routers/opportunities.py` | `opportunities` |
| Submit Opportunity | `submit.html` (legacy) | `routers/opportunities.py` | `opportunities` |
| **👍 Validation & Engagement** |
| Validate ("I Need This Too") | `pages/OpportunityDetail.tsx` | `routers/validations.py` | `validations` |
| Comments & Discussion | `pages/OpportunityDetail.tsx` | `routers/comments.py` | `comments` |
| Watchlist/Save | `pages/Saved.tsx` | `routers/watchlist.py` | `watchlist` |
| Follow Users/Categories | Various pages | `routers/follows.py` | `follows` |
| Share Opportunities | Share buttons | `routers/social.py` | `shares` |
| **🤖 AI Co-founder (Brain)** |
| Brain Dashboard | `pages/brain/BrainDashboard.tsx`<br/>`stores/brainStore.ts`<br/>`services/brainApi.ts` | `routers/brains.py` | `brains`<br/>`brain_opportunities`<br/>`brain_timeline` |
| Save to Brain | `pages/OpportunityDetail.tsx` | `routers/brains.py` | `brain_opportunities` |
| Brain Status Indicator | `components/Navbar.tsx` | `routers/brains.py` | `brains` |
| Timeline & History | `pages/brain/BrainDashboard.tsx` | `routers/brains.py` | `brain_timeline` |
| **🧠 AI Analysis & Matching** |
| DeepSeek Analysis | `pages/AIMatch.tsx`<br/>`services/deepseekApi.ts` | `routers/deepseek.py`<br/>`services/deepseek_service.py` | `brain_opportunities` |
| AI Match Scoring | `pages/AIMatch.tsx` | `routers/deepseek.py` | `brain_opportunities.match_score` |
| Idea Validation | `pages/IdeaEngine.tsx` | `routers/idea_engine.py`<br/>`routers/idea_validations.py` | `idea_validations` |
| AI Roadmap | `pages/AIRoadmap.tsx` | `routers/ai_engine.py` | `idea_validations` |
| AI Chat Interface | `pages/brain/*` | `routers/ai_chat.py` | `brains` |
| **💳 Payments & Subscriptions** |
| Pricing Page | `pages/Pricing.tsx`<br/>`pricing.html` (legacy) | `routers/subscriptions.py` | `subscriptions` |
| Checkout Flow | Stripe.js integration | `routers/subscriptions.py`<br/>`services/stripe_service.py` | `subscriptions`<br/>`transactions` |
| Subscription Management | `account.html` (legacy) | `routers/subscriptions.py` | `subscriptions` |
| Billing Portal | Redirect to Stripe | `routers/subscriptions.py` | `subscriptions` |
| Pay-per-Unlock | Opportunity detail | `routers/payments.py` | `transactions`<br/>`unlocked_opportunities` |
| Webhook Processing | N/A | `routers/stripe_webhook.py` | `stripe_events` |
| Usage Tracking | N/A | `services/usage_service.py` | `usage_records` |
| **👨‍💼 Expert Marketplace** |
| Browse Experts | `pages/ExpertMarketplace.tsx`<br/>`expert-marketplace.html` (legacy) | `routers/experts.py` | `experts`<br/>`user_profiles` |
| Expert Profile | `pages/ExpertProfile.tsx` | `routers/profiles.py` | `experts`<br/>`user_profiles` |
| Book Session | `expert-checkout.html` (legacy) | `routers/bookings.py` | `bookings` |
| Service Agreements | `agreement.html` (legacy) | `routers/agreements.py` | `agreements` |
| **📊 Analytics & Insights** |
| User Dashboard | `pages/Dashboard.tsx`<br/>`dashboard.html` (legacy) | `routers/analytics.py`<br/>`services/analytics_service.py` | `tracking_events`<br/>`usage_records` |
| Opportunity Analytics | Embedded in detail view | `routers/analytics.py` | `opportunities`<br/>`validations` |
| Feasibility Scoring | Various pages | `routers/analytics.py` | `opportunities.feasibility_score` |
| Growth Metrics | Dashboard | `routers/analytics.py` | `opportunities.validation_count` |
| **🔔 Notifications** |
| In-app Notifications | Navbar badge | `routers/notifications.py`<br/>`services/notification_service.py` | `notifications` |
| Email Notifications | N/A | `services/email_service.py` | `notifications` |
| Real-time Updates | WebSocket connection | `routers/websocket_router.py`<br/>`services/websocket_broadcaster.py` | N/A (in-memory) |
| **🛡️ Admin & Moderation** |
| Admin Panel | `admin.html` (legacy) | `routers/admin.py` | All tables |
| Content Moderation | Admin panel | `routers/moderation.py`<br/>`services/moderation_service.py` | `reports`<br/>`audit_logs` |
| User Management | Admin panel | `routers/admin.py` | `users` |
| Audit Logs | Admin panel | `routers/admin.py` | `audit_logs` |
| **👤 User Profile & Settings** |
| View Profile | `pages/Profile.tsx`<br/>`profile.html` (legacy) | `routers/profiles.py` | `user_profiles` |
| Edit Profile | Settings page | `routers/users.py` | `user_profiles` |
| Account Settings | `account.html` (legacy) | `routers/users.py` | `users` |
| Privacy Settings | Settings page | `routers/users.py` | `users` |

---

## 🔄 Data Flow Diagrams

### 1. Complete Authentication Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser
    participant ReactApp
    participant AuthStore
    participant FastAPI
    participant AuthRouter
    participant Database
    participant EmailService
    participant OAuthProvider

    %% Email/Password Flow
    User->>Browser: Visit /login
    Browser->>ReactApp: Load Login.tsx
    User->>ReactApp: Enter email + password
    ReactApp->>FastAPI: POST /api/v1/auth/login
    FastAPI->>AuthRouter: Route to auth.py
    AuthRouter->>Database: Query user by email
    Database-->>AuthRouter: User record
    AuthRouter->>AuthRouter: Verify password (bcrypt)

    alt Invalid Credentials
        AuthRouter-->>ReactApp: 401 Unauthorized
        ReactApp->>User: Show error message
    else Valid Credentials + 2FA Enabled
        AuthRouter->>Database: Check otp_enabled
        AuthRouter-->>ReactApp: 200 + requires_2fa: true
        ReactApp->>User: Show 2FA input
        User->>ReactApp: Enter TOTP code
        ReactApp->>FastAPI: POST /api/v1/auth/verify-2fa
        FastAPI->>AuthRouter: Verify TOTP
        alt Invalid TOTP
            AuthRouter-->>ReactApp: 401 Invalid code
        else Valid TOTP
            AuthRouter->>AuthRouter: Generate JWT
            AuthRouter-->>ReactApp: 200 + JWT token
        end
    else Valid Credentials + No 2FA
        AuthRouter->>AuthRouter: Generate JWT (python-jose)
        AuthRouter-->>ReactApp: 200 + JWT token + user data
    end

    ReactApp->>AuthStore: saveToken(jwt)
    AuthStore->>Browser: localStorage.setItem('token', jwt)
    AuthStore->>FastAPI: GET /api/v1/users/me (with JWT)
    FastAPI->>AuthRouter: Verify JWT
    AuthRouter->>Database: Get user details
    Database-->>AuthStore: Full user object
    AuthStore->>ReactApp: Update auth state
    ReactApp->>User: Redirect to /dashboard

    %% OAuth Flow
    Note over User,OAuthProvider: Alternative: OAuth Login
    User->>ReactApp: Click "Login with Google"
    ReactApp->>FastAPI: GET /api/v1/oauth/google
    FastAPI-->>Browser: Redirect to Google OAuth
    Browser->>OAuthProvider: Authorization request
    User->>OAuthProvider: Grant permission
    OAuthProvider->>FastAPI: Redirect to /api/v1/oauth/callback?code=xxx
    FastAPI->>OAuthProvider: Exchange code for token
    OAuthProvider-->>FastAPI: Access token + user info
    FastAPI->>Database: Find or create user
    FastAPI->>AuthRouter: Generate JWT
    FastAPI-->>Browser: Redirect to /auth/callback?token=jwt
    Browser->>ReactApp: Load AuthCallback.tsx
    ReactApp->>AuthStore: saveToken(jwt)
    AuthStore->>Browser: localStorage.setItem('token', jwt)
    ReactApp->>User: Redirect to /dashboard

    %% Magic Link Flow
    Note over User,EmailService: Alternative: Magic Link
    User->>ReactApp: Click "Send magic link"
    User->>ReactApp: Enter email
    ReactApp->>FastAPI: POST /api/v1/auth/magic-link
    FastAPI->>Database: Create magic_link_token
    FastAPI->>EmailService: Send email with link
    EmailService-->>User: Email delivered
    User->>Browser: Click link in email
    Browser->>FastAPI: GET /api/v1/auth/magic-link/verify?token=xxx
    FastAPI->>Database: Verify token & expiry
    FastAPI->>AuthRouter: Generate JWT
    FastAPI-->>Browser: Redirect to /auth/magic?token=jwt
    Browser->>ReactApp: Load MagicLinkCallback.tsx
    ReactApp->>AuthStore: saveToken(jwt)
    ReactApp->>User: Redirect to /dashboard
```

### 2. AI Brain + DeepSeek Analysis Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser
    participant OpportunityDetail
    participant DeepSeekAPI as DeepSeek API Client
    participant BrainAPI as Brain API Client
    participant FastAPI
    participant DeepSeekRouter
    participant DeepSeekService
    participant BrainRouter
    participant Database
    participant DeepSeekExternal as DeepSeek AI

    User->>Browser: View opportunity detail
    Browser->>OpportunityDetail: Load page
    OpportunityDetail->>BrainAPI: GET /api/v1/brains/active
    FastAPI->>BrainRouter: Get active brain
    BrainRouter->>Database: Query user's active brain
    Database-->>OpportunityDetail: Active brain data

    User->>OpportunityDetail: Click "Analyze with AI"
    OpportunityDetail->>DeepSeekAPI: POST /api/v1/deepseek/analyze<br/>{opportunity_id, brain_id}

    FastAPI->>DeepSeekRouter: Route to deepseek.py
    DeepSeekRouter->>Database: Get opportunity details
    DeepSeekRouter->>Database: Get brain config & state
    Database-->>DeepSeekRouter: Opportunity + Brain data

    DeepSeekRouter->>DeepSeekService: analyze_opportunity()
    DeepSeekService->>DeepSeekService: Build analysis prompt<br/>with brain context
    DeepSeekService->>DeepSeekExternal: POST /chat/completions<br/>{"model": "deepseek-chat"}

    DeepSeekExternal-->>DeepSeekService: Analysis response<br/>+ match_score + reasoning

    DeepSeekService->>DeepSeekService: Calculate token usage<br/>& cost
    DeepSeekService-->>DeepSeekRouter: Analysis result<br/>{match_score, reasoning, tokens, cost}

    DeepSeekRouter->>Database: Store analysis result<br/>in brain_opportunities
    DeepSeekRouter-->>OpportunityDetail: 200 + analysis data

    OpportunityDetail->>User: Display match score<br/>+ reasoning

    User->>OpportunityDetail: Click "Save to Brain"
    OpportunityDetail->>BrainAPI: POST /api/v1/brains/opportunities<br/>{brain_id, opportunity_id, match_score}

    FastAPI->>BrainRouter: Add to brain
    BrainRouter->>Database: INSERT brain_opportunities
    BrainRouter->>Database: INSERT brain_timeline event
    BrainRouter->>Database: UPDATE brain.state (increment counts)
    BrainRouter-->>OpportunityDetail: 201 Created

    OpportunityDetail->>User: Show "Saved to Brain ✓"

    Note over User,Database: Brain now tracks this opportunity
```

### 3. Stripe Payment & Subscription Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser
    participant PricingPage
    participant FastAPI
    participant SubRouter as Subscription Router
    participant StripeService
    participant Database
    participant StripeAPI
    participant StripeCheckout
    participant WebhookRouter

    User->>Browser: Visit /pricing
    Browser->>PricingPage: Display plans
    User->>PricingPage: Click "Upgrade to Pro"

    PricingPage->>FastAPI: POST /api/v1/subscriptions/checkout<br/>{tier: "PRO", success_url, cancel_url}

    FastAPI->>SubRouter: Create checkout session
    SubRouter->>Database: Get or create user
    SubRouter->>Database: Check existing subscription

    SubRouter->>StripeService: create_checkout_session()
    StripeService->>StripeAPI: GET /customers?email=xxx

    alt Customer Exists
        StripeAPI-->>StripeService: customer_id
    else New Customer
        StripeService->>StripeAPI: POST /customers
        StripeAPI-->>StripeService: customer_id
        StripeService->>Database: UPDATE users<br/>SET stripe_customer_id
    end

    StripeService->>StripeAPI: POST /checkout/sessions<br/>{customer, mode: "subscription",<br/>line_items: [{price: PRO_PRICE_ID}]}

    StripeAPI-->>StripeService: session {url, id}
    StripeService-->>SubRouter: Checkout session
    SubRouter-->>PricingPage: {checkout_url}

    PricingPage->>Browser: Redirect to checkout_url
    Browser->>StripeCheckout: Load Stripe Checkout page

    User->>StripeCheckout: Enter card details
    StripeCheckout->>StripeAPI: Process payment

    alt Card Declined
        StripeAPI-->>User: Error: Card declined
    else 3D Secure Required
        StripeCheckout->>User: 3DS verification modal
        User->>StripeCheckout: Complete 3DS
    end

    StripeAPI->>StripeAPI: Create subscription
    StripeAPI-->>User: Redirect to success_url

    StripeAPI->>WebhookRouter: POST /api/v1/webhook/stripe<br/>Event: checkout.session.completed

    WebhookRouter->>WebhookRouter: Verify signature<br/>(Stripe-Signature header)
    WebhookRouter->>StripeService: handle_webhook(event)

    StripeService->>StripeAPI: GET /checkout/sessions/{session_id}
    StripeAPI-->>StripeService: session with subscription_id

    StripeService->>Database: Find user by stripe_customer_id
    StripeService->>Database: INSERT OR UPDATE subscriptions<br/>SET tier="PRO", status="ACTIVE",<br/>stripe_subscription_id,<br/>current_period_start, current_period_end

    StripeService->>Database: INSERT stripe_events<br/>(idempotency)
    StripeService->>Database: INSERT audit_log
    StripeService-->>WebhookRouter: Success
    WebhookRouter-->>StripeAPI: 200 OK

    Browser->>PricingPage: Lands on success_url
    PricingPage->>FastAPI: GET /api/v1/users/me
    FastAPI->>Database: Get user with subscription
    Database-->>PricingPage: User {tier: "PRO"}
    PricingPage->>User: "Welcome to Pro! 🎉"

    Note over User,Database: User now has Pro access
```

### 4. Opportunity Submission with Duplicate Detection

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser
    participant SubmitPage
    participant FastAPI
    participant OppRouter
    participant Database
    participant AIService
    participant ModService as Moderation Service
    participant EmailService

    User->>Browser: Click "Submit Opportunity"
    Browser->>SubmitPage: Load submit form

    User->>SubmitPage: Fill form<br/>(title, description, category,<br/>severity, location, etc.)
    User->>SubmitPage: Click "Submit"

    SubmitPage->>SubmitPage: Client-side validation

    alt Validation Fails
        SubmitPage->>User: Show field errors
    else Validation Passes
        SubmitPage->>FastAPI: POST /api/v1/opportunities/<br/>{title, description, category, ...}

        FastAPI->>OppRouter: Create opportunity
        OppRouter->>OppRouter: Server-side validation<br/>(Pydantic schema)

        alt Invalid Data
            OppRouter-->>SubmitPage: 400 Bad Request
            SubmitPage->>User: Show errors
        else Valid Data
            OppRouter->>ModService: check_content(title, description)
            ModService->>ModService: Profanity filter<br/>Spam detection

            alt Content Flagged
                ModService-->>OppRouter: Flagged
                OppRouter-->>SubmitPage: 422 Content policy violation
                SubmitPage->>User: Show moderation message
            else Content OK
                OppRouter->>Database: SELECT opportunities<br/>WHERE title SIMILAR
                Database-->>OppRouter: Similar opportunities

                OppRouter->>OppRouter: Calculate Jaccard similarity<br/>for each result

                alt Similarity > 50%
                    OppRouter-->>SubmitPage: 200 + duplicate_warning<br/>{similar: [top 5 matches]}
                    SubmitPage->>User: Show duplicate modal<br/>"Similar opportunities found"

                    User->>SubmitPage: Click action
                    alt User: "Validate Existing"
                        SubmitPage->>FastAPI: POST /api/v1/validations/<br/>{opportunity_id: existing_id}
                        FastAPI->>Database: INSERT validation
                        FastAPI->>Database: UPDATE opportunity<br/>validation_count++
                        FastAPI-->>SubmitPage: 201 Created
                        SubmitPage->>Browser: Redirect to existing opportunity
                    else User: "Submit Anyway"
                        SubmitPage->>FastAPI: POST /api/v1/opportunities/<br/>{...data, force: true}
                        Note over OppRouter: Skip duplicate check
                    else User: "Cancel"
                        SubmitPage->>User: Return to form
                    end
                end

                OppRouter->>Database: INSERT INTO opportunities
                Database-->>OppRouter: opportunity_id

                OppRouter->>Database: INSERT INTO validations<br/>(auto-validate by submitter)

                OppRouter->>OppRouter: Calculate initial<br/>feasibility_score
                OppRouter->>Database: UPDATE opportunity<br/>SET feasibility_score

                OppRouter->>Database: SELECT users<br/>WHERE follows category
                Database-->>OppRouter: Category followers

                OppRouter->>EmailService: send_notification_emails()<br/>(async task)
                EmailService->>Database: INSERT notifications

                OppRouter-->>SubmitPage: 201 Created<br/>{opportunity}
                SubmitPage->>Browser: Redirect to /opportunity/{id}
                Browser->>User: Show opportunity detail
            end
        end
    end
```

---

## 🔒 Security Architecture

### Security Layers & Controls

```mermaid
graph TB
    Internet([Internet Traffic])

    subgraph "Layer 1: Network Security"
        HTTPS[HTTPS/TLS Encryption]
        Firewall[Replit Firewall]
    end

    subgraph "Layer 2: Application Security"
        CORS[CORS Middleware<br/>Allowed Origins]
        RateLimit[Rate Limiting<br/>Per IP + User]
        SecurityHeaders[Security Headers<br/>X-Frame-Options, CSP, etc.]
    end

    subgraph "Layer 3: Authentication"
        JWT[JWT Verification<br/>python-jose]
        OAuth[OAuth 2.0<br/>Google, GitHub, Replit]
        MagicLink[Magic Links<br/>Time-limited tokens]
        TwoFA[2FA/TOTP<br/>pyotp]
    end

    subgraph "Layer 4: Authorization"
        Permissions[Permission Checks<br/>Owner/Admin/User]
        TierCheck[Subscription Tier Gates]
        UsageLimit[Usage Quotas<br/>Free vs Pro limits]
    end

    subgraph "Layer 5: Data Security"
        PasswordHash[bcrypt Password Hashing<br/>Cost factor: 12]
        SQLInjection[SQL Injection Protection<br/>ORM Parameterization]
        XSS[XSS Protection<br/>Input Sanitization]
        CSRF[CSRF Protection<br/>SameSite cookies]
    end

    subgraph "Layer 6: Sensitive Data"
        Secrets[Environment Secrets<br/>Encrypted storage]
        NoCardData[PCI Compliance<br/>No card data stored]
        StripeTokens[Stripe Tokenization<br/>Only IDs stored]
        AuditLog[Audit Logging<br/>All actions tracked]
    end

    subgraph "Layer 7: Content Security"
        Moderation[Content Moderation<br/>Profanity + Spam filters]
        ReportSystem[User Reporting<br/>Flagging system]
        AdminReview[Admin Review Queue]
    end

    Internet --> HTTPS
    HTTPS --> Firewall
    Firewall --> CORS
    CORS --> RateLimit
    RateLimit --> SecurityHeaders
    SecurityHeaders --> JWT
    JWT --> OAuth
    OAuth --> MagicLink
    MagicLink --> TwoFA
    TwoFA --> Permissions
    Permissions --> TierCheck
    TierCheck --> UsageLimit
    UsageLimit --> PasswordHash
    PasswordHash --> SQLInjection
    SQLInjection --> XSS
    XSS --> CSRF
    CSRF --> Secrets
    Secrets --> NoCardData
    NoCardData --> StripeTokens
    StripeTokens --> AuditLog
    AuditLog --> Moderation
    Moderation --> ReportSystem
    ReportSystem --> AdminReview

    style HTTPS fill:#4caf50,stroke:#2e7d32
    style JWT fill:#ff9800,stroke:#e65100
    style PasswordHash fill:#f44336,stroke:#b71c1c
    style NoCardData fill:#2196f3,stroke:#0d47a1
```

### Authentication Methods Comparison

| Method | Security Level | UX Friction | Implementation | Use Case |
|--------|---------------|-------------|----------------|----------|
| **Email + Password** | 🔒🔒🔒 Medium | Medium | `routers/auth.py` | Standard login |
| **Email + Password + 2FA** | 🔒🔒🔒🔒 High | High | `routers/two_factor.py` | High-security accounts |
| **Google OAuth** | 🔒🔒🔒🔒 High | Low | `routers/oauth.py` | Quick registration |
| **GitHub OAuth** | 🔒🔒🔒🔒 High | Low | `routers/oauth.py` | Developer users |
| **Magic Link** | 🔒🔒🔒 Medium | Very Low | `routers/magic_link.py` | Passwordless login |
| **Replit Auth** | 🔒🔒🔒 Medium | Very Low | `routers/replit_auth.py` | Replit platform users |

---

## 🚀 Deployment Architecture

### Replit Deployment Model

```mermaid
graph TB
    subgraph "Replit Cloud Platform"
        subgraph "Container Runtime"
            MainProcess[server.py<br/>Main Process]

            Thread1[Thread 1<br/>Frontend Server<br/>Port 5000<br/>SimpleHTTPRequestHandler]

            Thread2[Thread 2<br/>Backend Server<br/>Port 8000<br/>Uvicorn + FastAPI]

            MainProcess -->|spawn| Thread1
            MainProcess -->|spawn| Thread2
            MainProcess -->|health check| Thread2
        end

        subgraph "Managed Database"
            ReplDB[(Replit PostgreSQL<br/>Managed Service<br/>Auto-backups)]
        end

        subgraph "File System"
            StaticFiles[Static HTML/CSS/JS<br/>Root directory]
            ReactDist[React Build<br/>frontend/dist/]
            BackendCode[Python Backend<br/>backend/app/]
        end

        subgraph "Environment Management"
            Secrets[Replit Secrets<br/>STRIPE_SECRET_KEY<br/>DATABASE_URL<br/>SECRET_KEY<br/>etc.]
        end
    end

    subgraph "External Network"
        ReplDomain[Replit Domain<br/>*.repl.co]
        CustomDomain[Custom Domain<br/>(optional)]
    end

    Internet([Internet Users])

    Internet --> ReplDomain
    Internet --> CustomDomain

    ReplDomain --> Thread1
    CustomDomain --> Thread1

    Thread1 -->|serve static| StaticFiles
    Thread1 -->|serve React| ReactDist
    Thread1 -->|proxy /api/*| Thread2

    Thread2 -->|read| Secrets
    Thread2 -->|SQL queries| ReplDB
    Thread2 -->|execute| BackendCode

    style MainProcess fill:#f57c00,stroke:#e65100
    style Thread1 fill:#42a5f5,stroke:#1976d2
    style Thread2 fill:#66bb6a,stroke:#388e3c
    style ReplDB fill:#5e35b1,stroke:#4527a0
    style Secrets fill:#ffa726,stroke:#f57c00
```

### Port Configuration

| Port | Service | Protocol | Purpose |
|------|---------|----------|---------|
| **5000** | Frontend Server | HTTP | Serve static HTML/CSS/JS & React app |
| **8000** | Backend API | HTTP | FastAPI REST API + WebSocket |
| **5432** | PostgreSQL | TCP | Database connections (internal) |
| **5173** | Vite Dev Server | HTTP | Development React server (dev only) |

### Environment Variables

```bash
# Application Core
SECRET_KEY=<256-bit-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
# OR for Replit managed DB:
REPLIT_DB_URL=<auto-injected>

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5000","https://*.repl.co"]
FRONTEND_URL=https://friction.repl.co

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_PRO=price_xxx
STRIPE_PRICE_BUSINESS=price_xxx

# OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx

# Email
RESEND_API_KEY=re_xxx
FROM_EMAIL=noreply@friction.app

# AI Services
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx

# Monitoring (optional)
SENTRY_DSN=https://xxx@sentry.io/xxx
LOG_LEVEL=INFO
```

---

## 📈 System Metrics & Monitoring

### Key Performance Indicators

| Metric | Target | Monitoring |
|--------|--------|------------|
| **API Response Time (p95)** | < 200ms | Sentry Performance |
| **Database Query Time (avg)** | < 50ms | SQLAlchemy logging |
| **Frontend Load Time** | < 2s | Browser DevTools |
| **WebSocket Latency** | < 100ms | Custom metrics |
| **Uptime** | > 99.5% | Replit status |
| **Error Rate** | < 0.1% | Sentry error tracking |

### Scalability Considerations

```mermaid
graph LR
    subgraph "Current (MVP)"
        SingleContainer[Single Replit Container<br/>2 threads]
        SingleDB[(Single PostgreSQL)]
    end

    subgraph "Future Scale (Phase 2)"
        LoadBalancer[Load Balancer]
        API1[API Instance 1]
        API2[API Instance 2]
        API3[API Instance N]
        PrimaryDB[(Primary DB)]
        ReadReplica1[(Read Replica 1)]
        ReadReplica2[(Read Replica 2)]
        RedisCache[(Redis Cache)]
        CDN[CDN for Static Assets]
    end

    SingleContainer --> LoadBalancer
    SingleDB --> PrimaryDB

    LoadBalancer --> API1
    LoadBalancer --> API2
    LoadBalancer --> API3

    API1 --> RedisCache
    API2 --> RedisCache
    API3 --> RedisCache

    API1 --> PrimaryDB
    API2 --> ReadReplica1
    API3 --> ReadReplica2

    PrimaryDB -.->|Replication| ReadReplica1
    PrimaryDB -.->|Replication| ReadReplica2

    style SingleContainer fill:#90caf9
    style LoadBalancer fill:#66bb6a
    style RedisCache fill:#ef5350
```

---

## 🎓 Development Workflow

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/friction.git
cd friction

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp ../.env.example backend/.env
# Edit backend/.env with your credentials

# Run database migrations
alembic upgrade head

# Start backend server
cd ..
python server.py  # Starts both frontend + backend

# 3. Setup React frontend (in new terminal)
cd frontend
npm install
npm run dev  # Vite dev server on port 5173
```

### Git Branching Strategy

```mermaid
gitGraph
    commit id: "Initial commit"
    branch develop
    checkout develop
    commit id: "Add auth system"
    commit id: "Add opportunities"

    branch feature/brain
    checkout feature/brain
    commit id: "Add brain models"
    commit id: "Add brain API"
    checkout develop
    merge feature/brain

    branch feature/stripe
    checkout feature/stripe
    commit id: "Add Stripe integration"
    commit id: "Add webhooks"
    checkout develop
    merge feature/stripe

    checkout main
    merge develop tag: "v1.0.0"

    checkout develop
    commit id: "Bug fixes"
    checkout main
    merge develop tag: "v1.0.1"
```

---

## 📚 API Documentation

### API Endpoint Summary

| Category | Endpoint Count | Base Path |
|----------|---------------|-----------|
| **Authentication** | 12 | `/api/v1/auth/*` |
| **Opportunities** | 8 | `/api/v1/opportunities/*` |
| **AI Features** | 15 | `/api/v1/brains/*`, `/api/v1/deepseek/*`, `/api/v1/idea-*` |
| **Payments** | 7 | `/api/v1/subscriptions/*`, `/api/v1/payments/*` |
| **Social** | 10 | `/api/v1/validations/*`, `/api/v1/comments/*`, `/api/v1/follows/*` |
| **Admin** | 6 | `/api/v1/admin/*` |
| **Analytics** | 5 | `/api/v1/analytics/*` |
| **Marketplace** | 8 | `/api/v1/experts/*`, `/api/v1/agreements/*` |
| **Utilities** | 4 | `/api/v1/contact`, `/api/v1/notifications/*` |
| **WebSocket** | 1 | `/ws` |

**Total: ~76 API endpoints**

### Quick API Reference

```yaml
# Authentication
POST   /api/v1/auth/register              # Create account
POST   /api/v1/auth/login                 # Email/password login
POST   /api/v1/auth/verify-email          # Verify email
POST   /api/v1/auth/magic-link            # Request magic link
GET    /api/v1/oauth/google               # Google OAuth
GET    /api/v1/oauth/github               # GitHub OAuth
POST   /api/v1/auth/2fa/enable            # Enable 2FA
POST   /api/v1/auth/2fa/verify            # Verify 2FA code

# Opportunities
GET    /api/v1/opportunities/             # List (with filters)
POST   /api/v1/opportunities/             # Create
GET    /api/v1/opportunities/{id}         # Get detail
PUT    /api/v1/opportunities/{id}         # Update
DELETE /api/v1/opportunities/{id}         # Delete
GET    /api/v1/opportunities/search       # Full-text search

# Validations & Engagement
POST   /api/v1/validations/               # Validate opportunity
DELETE /api/v1/validations/{id}           # Remove validation
POST   /api/v1/comments/                  # Add comment
GET    /api/v1/comments/{opp_id}          # Get comments
POST   /api/v1/watchlist/                 # Add to watchlist
DELETE /api/v1/watchlist/{id}             # Remove from watchlist

# AI Co-founder (Brain)
GET    /api/v1/brains/active              # Get active brain
POST   /api/v1/brains/                    # Create brain
PUT    /api/v1/brains/{id}                # Update brain
POST   /api/v1/brains/opportunities       # Save to brain
GET    /api/v1/brains/{id}/timeline       # Get timeline

# DeepSeek AI
POST   /api/v1/deepseek/analyze           # Analyze opportunity
POST   /api/v1/deepseek/match             # Match opportunities

# Idea Validation
POST   /api/v1/idea-engine/submit         # Submit idea
POST   /api/v1/idea-validations/          # Create validation
GET    /api/v1/idea-validations/{id}      # Get validation result

# Payments & Subscriptions
POST   /api/v1/subscriptions/checkout     # Create checkout
POST   /api/v1/subscriptions/portal       # Billing portal
POST   /api/v1/subscriptions/cancel       # Cancel subscription
GET    /api/v1/subscriptions/me           # Get my subscription
POST   /api/v1/payments/unlock            # Pay-per-unlock
POST   /webhook/stripe                    # Stripe webhooks

# Analytics
GET    /api/v1/analytics/opportunities    # Opportunity stats
GET    /api/v1/analytics/feasibility      # Feasibility analysis
GET    /api/v1/analytics/geographic       # Geographic distribution

# Expert Marketplace
GET    /api/v1/experts/                   # List experts
GET    /api/v1/experts/{id}               # Expert profile
POST   /api/v1/bookings/                  # Book session
GET    /api/v1/agreements/{id}            # Get agreement

# User Management
GET    /api/v1/users/me                   # Get current user
PUT    /api/v1/users/me                   # Update profile
GET    /api/v1/users/{id}/profile         # Public profile

# Admin
GET    /api/v1/admin/stats                # System stats
GET    /api/v1/admin/users                # User management
POST   /api/v1/moderation/review          # Review content
GET    /api/v1/audit-logs/                # Audit trail

# WebSocket
WS     /ws                                 # Real-time updates
```

---

## 🏁 Conclusion

This document provides a comprehensive overview of the Friction (OppGrid) system architecture, covering:

✅ Complete system architecture with all components
✅ Technology stack for frontend, backend, and infrastructure
✅ Frontend architecture (React + legacy HTML)
✅ Backend architecture (30+ routers, services, models)
✅ Database schema with 20+ tables
✅ Feature-to-code mapping for all major features
✅ Detailed data flow diagrams (authentication, AI, payments, submissions)
✅ Security architecture with 7 layers of protection
✅ Deployment architecture on Replit
✅ API documentation with ~76 endpoints

### Key Takeaways

1. **Hybrid Frontend**: Modern React app + legacy HTML pages
2. **Comprehensive Backend**: 30+ API routers, 15+ services, 20+ models
3. **AI-Powered**: DeepSeek AI integration for opportunity analysis
4. **Payment-Ready**: Full Stripe integration with subscriptions + pay-per-unlock
5. **Scalable**: Built on FastAPI with async support, ready to scale
6. **Secure**: 7-layer security architecture with OAuth, 2FA, and audit logging

---

**Document Version:** 2.0
**Last Updated:** 2025-12-20
**Maintained By:** Development Team
**Next Review:** 2025-01-20
