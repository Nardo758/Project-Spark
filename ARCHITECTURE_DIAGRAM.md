# FRICTION - System Architecture & Flow Diagrams

## Application Overview

**Name:** Friction (OppGrid API)
**Purpose:** Problem discovery search engine and platform for discovering, validating, and tracking real-world problems and unmet needs.

---

## 1. HIGH-LEVEL SYSTEM ARCHITECTURE

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[User Browser]
        HTML[HTML Pages<br/>index.html, signin.html, pricing.html]
        JS[JavaScript Layer<br/>app.js, api.js, auth.js]
        StripeJS[Stripe.js SDK]
    end

    subgraph "Server Layer - Port 5000"
        Proxy[Proxy Server<br/>server.py<br/>SimpleHTTPRequestHandler]
    end

    subgraph "Backend Layer - Port 8000"
        FastAPI[FastAPI Application]

        subgraph "23 API Routers"
            Auth[auth.py - Authentication]
            Opp[opportunities.py - CRUD]
            Sub[subscriptions.py - Payments]
            Idea[idea_engine.py - AI Validation]
            Analytics[analytics.py - Insights]
            Admin[admin.py - Management]
            OAuth[oauth.py - Social Login]
            Other[... 16 more routers]
        end

        subgraph "11 Services"
            StripeService[stripe_service.py]
            EmailService[email_service.py]
            UsageService[usage_service.py]
            AIService[ai_analysis.py]
            ModService[moderation.py]
            OtherServices[... 6 more services]
        end

        subgraph "12+ Data Models"
            UserModel[User Model]
            OppModel[Opportunity Model]
            SubModel[Subscription Model]
            ValidationModel[Validation Model]
            CommentModel[Comment Model]
            UnlockedModel[UnlockedOpportunity Model]
            UsageModel[UsageRecord Model]
            OtherModels[... 5 more models]
        end
    end

    subgraph "Database Layer"
        PostgreSQL[(PostgreSQL<br/>Replit Managed)]
    end

    subgraph "External Services"
        StripeAPI[Stripe API<br/>Payments & Subscriptions]
        GoogleOAuth[Google OAuth]
        GitHubOAuth[GitHub OAuth]
        ResendAPI[Resend Email API]
    end

    Browser --> HTML
    HTML --> JS
    JS --> StripeJS
    JS -->|HTTP/HTTPS| Proxy
    Proxy -->|Static Files| Browser
    Proxy -->|/api/* requests| FastAPI

    FastAPI --> Auth
    FastAPI --> Opp
    FastAPI --> Sub
    FastAPI --> Idea
    FastAPI --> Analytics
    FastAPI --> Admin
    FastAPI --> OAuth
    FastAPI --> Other

    Auth --> StripeService
    Sub --> StripeService
    Idea --> StripeService
    Opp --> EmailService
    Auth --> EmailService
    Opp --> UsageService
    Sub --> UsageService
    Opp --> AIService

    StripeService --> UserModel
    StripeService --> SubModel
    StripeService --> UnlockedModel
    Auth --> UserModel
    Opp --> OppModel
    Opp --> ValidationModel
    Opp --> CommentModel
    UsageService --> UsageModel

    UserModel -->|SQLAlchemy ORM| PostgreSQL
    OppModel -->|SQLAlchemy ORM| PostgreSQL
    SubModel -->|SQLAlchemy ORM| PostgreSQL
    ValidationModel -->|SQLAlchemy ORM| PostgreSQL
    CommentModel -->|SQLAlchemy ORM| PostgreSQL
    UnlockedModel -->|SQLAlchemy ORM| PostgreSQL
    UsageModel -->|SQLAlchemy ORM| PostgreSQL
    OtherModels -->|SQLAlchemy ORM| PostgreSQL

    StripeService -->|API Calls| StripeAPI
    StripeAPI -->|Webhooks| Sub
    OAuth -->|OAuth Flow| GoogleOAuth
    OAuth -->|OAuth Flow| GitHubOAuth
    EmailService -->|Send Emails| ResendAPI

    style Browser fill:#e1f5ff
    style PostgreSQL fill:#ffebee
    style StripeAPI fill:#fff9c4
    style FastAPI fill:#e8f5e9
```

---

## 2. USER FLOW & JOURNEY

### 2.1 Authentication Flow

```mermaid
flowchart TD
    Start([User Visits App]) --> LandingPage[Landing Page<br/>index.html]
    LandingPage --> CheckAuth{Authenticated?}

    CheckAuth -->|No| GuestMode[Guest Mode<br/>Limited Features]
    CheckAuth -->|Yes| Dashboard[Full Dashboard Access]

    GuestMode --> NeedAuth{Action Requires<br/>Authentication?}
    NeedAuth -->|Yes| SignInChoice[Redirect to Sign In]
    NeedAuth -->|No| Continue[Continue as Guest]

    SignInChoice --> SignInPage[signin.html]
    SignInPage --> AuthMethod{Choose Auth Method}

    AuthMethod -->|Email/Password| EmailLogin[Enter Credentials]
    AuthMethod -->|Google| GoogleOAuth[Google OAuth Flow]
    AuthMethod -->|GitHub| GitHubOAuth[GitHub OAuth Flow]
    AuthMethod -->|Magic Link| MagicLink[Enter Email]

    EmailLogin --> ValidateCreds{Valid?}
    ValidateCreds -->|No| LoginError[Show Error<br/>Retry]
    ValidateCreds -->|Yes| Check2FA{2FA Enabled?}

    Check2FA -->|Yes| Enter2FA[Enter TOTP Code]
    Check2FA -->|No| IssueJWT[Issue JWT Token]

    Enter2FA --> Verify2FA{Valid Code?}
    Verify2FA -->|No| TwoFAError[Invalid Code<br/>Retry]
    Verify2FA -->|Yes| IssueJWT

    GoogleOAuth --> OAuthCallback[OAuth Callback]
    GitHubOAuth --> OAuthCallback
    MagicLink --> SendEmail[Send Magic Link Email]
    SendEmail --> ClickLink[User Clicks Link]
    ClickLink --> OAuthCallback

    OAuthCallback --> CreateOrLink{User Exists?}
    CreateOrLink -->|No| CreateAccount[Create New Account]
    CreateOrLink -->|Yes| LinkAccount[Link OAuth Account]

    CreateAccount --> IssueJWT
    LinkAccount --> IssueJWT

    IssueJWT --> StoreToken[Store JWT in localStorage]
    StoreToken --> RedirectDashboard[Redirect to Dashboard]
    RedirectDashboard --> Dashboard

    LoginError --> SignInPage
    TwoFAError --> Enter2FA

    Dashboard --> SessionExpired{Token Expired?}
    SessionExpired -->|Yes| RefreshPrompt[Prompt Re-login]
    SessionExpired -->|No| ContinueSession[Continue Session]

    RefreshPrompt --> SignInPage

    style Start fill:#e1f5ff
    style Dashboard fill:#c8e6c9
    style IssueJWT fill:#fff9c4
    style LoginError fill:#ffcdd2
    style TwoFAError fill:#ffcdd2
```

### 2.2 Core User Journey - Problem Discovery & Validation

```mermaid
flowchart TD
    Start([User Enters App]) --> Browse[Browse Opportunities<br/>Consumer Tab]

    Browse --> ViewOptions{User Action}

    ViewOptions -->|Filter| ApplyFilters[Apply Filters:<br/>Category, Geography,<br/>Feasibility Score]
    ViewOptions -->|Search| SearchBox[Enter Keywords<br/>Full-Text Search]
    ViewOptions -->|Click Card| ViewDetail[View Opportunity Detail]

    ApplyFilters --> UpdateResults[Update Results List]
    SearchBox --> UpdateResults
    UpdateResults --> Browse

    ViewDetail --> DetailPage[opportunity.html<br/>Show Full Details]
    DetailPage --> DetailActions{User Action}

    DetailActions -->|Validate| CheckLogin{Logged In?}
    DetailActions -->|Comment| CheckLogin
    DetailActions -->|Save to Watchlist| CheckLogin
    DetailActions -->|Share| ShareModal[Open Share Modal]
    DetailActions -->|View More| RelatedOpp[Show Related Opportunities]

    CheckLogin -->|No| RedirectSignIn[Redirect to Sign In]
    CheckLogin -->|Yes| PerformAction{Action Type}

    PerformAction -->|Validate| AlreadyValidated{Already<br/>Validated?}
    PerformAction -->|Comment| AddComment[Add Comment]
    PerformAction -->|Watchlist| AddToWatchlist[Add to Watchlist]

    AlreadyValidated -->|Yes| RemoveValidation[Remove Validation<br/>DELETE /api/v1/validations/{id}]
    AlreadyValidated -->|No| CreateValidation[POST /api/v1/validations/<br/>opportunity_id]

    CreateValidation --> UpdateCount[Increment Validation Count<br/>Update Feasibility Score]
    RemoveValidation --> DecreaseCount[Decrease Validation Count]

    UpdateCount --> UpdateUI[Update UI:<br/>Button → "Validated ✓"<br/>Show New Count]
    DecreaseCount --> UpdateUI2[Update UI:<br/>Button → "I Need This Too"<br/>Show New Count]

    AddComment --> PostComment[POST /api/v1/comments/<br/>content, opportunity_id]
    PostComment --> RefreshComments[Refresh Comments Section]

    AddToWatchlist --> PostWatchlist[POST /api/v1/watchlist/<br/>opportunity_id]
    PostWatchlist --> WatchlistSuccess[Show Success Message]

    ShareModal --> ShareOptions{Share Method}
    ShareOptions -->|Twitter| ShareTwitter[Open Twitter Share]
    ShareOptions -->|LinkedIn| ShareLinkedIn[Open LinkedIn Share]
    ShareOptions -->|Copy Link| CopyLink[Copy URL to Clipboard]

    RelatedOpp --> Browse
    RedirectSignIn --> SignInFlow[Sign In Flow]
    SignInFlow --> DetailPage

    UpdateUI --> DetailPage
    UpdateUI2 --> DetailPage
    RefreshComments --> DetailPage
    WatchlistSuccess --> DetailPage

    style Start fill:#e1f5ff
    style UpdateCount fill:#c8e6c9
    style PostComment fill:#c8e6c9
    style RedirectSignIn fill:#fff9c4
```

### 2.3 Problem Submission Flow with Duplicate Detection

```mermaid
flowchart TD
    Start([User Clicks "Share a Friction"]) --> CheckAuth{Authenticated?}

    CheckAuth -->|No| RedirectSignIn[Redirect to Sign In]
    CheckAuth -->|Yes| SubmitForm[Submit Opportunity Form<br/>Submit Tab]

    RedirectSignIn --> SignIn[Complete Sign In]
    SignIn --> SubmitForm

    SubmitForm --> FillForm[Fill Form Fields:<br/>Title, Description,<br/>Category, Severity,<br/>Geographic Scope,<br/>Location, Anonymous]

    FillForm --> SubmitButton[Click Submit]
    SubmitButton --> ClientValidation{Client-Side<br/>Validation}

    ClientValidation -->|Invalid| ShowErrors[Show Form Errors]
    ShowErrors --> FillForm

    ClientValidation -->|Valid| SendToBackend[POST /api/v1/opportunities/<br/>opportunity data]

    SendToBackend --> ServerValidation{Server-Side<br/>Validation}

    ServerValidation -->|Invalid| ReturnError[Return 400 Error]
    ReturnError --> ShowErrors

    ServerValidation -->|Valid| DuplicateCheck[Check for Duplicates<br/>Jaccard Similarity Algorithm]

    DuplicateCheck --> SimilarityScore{Similarity > 50%?}

    SimilarityScore -->|No| CreateOpp[Create New Opportunity]
    SimilarityScore -->|Yes| ShowDuplicates[Show Duplicate Warning Modal<br/>Top 5 Similar Opportunities]

    ShowDuplicates --> UserChoice{User Decision}

    UserChoice -->|Validate Existing| ValidateExisting[POST /api/v1/validations/<br/>existing opportunity_id]
    UserChoice -->|Submit Anyway| CreateOpp
    UserChoice -->|Cancel| SubmitForm

    ValidateExisting --> UpdateValidation[Increment Validation Count]
    UpdateValidation --> RedirectToExisting[Redirect to Existing<br/>Opportunity Detail]

    CreateOpp --> InsertDB[INSERT INTO opportunities<br/>Database Operation]
    InsertDB --> AutoValidate[Auto-Validate by Submitter<br/>INSERT INTO validations]
    AutoValidate --> CalculateFeasibility[Calculate Initial<br/>Feasibility Score]
    CalculateFeasibility --> NotifyFollowers[Notify Relevant Followers<br/>Category Watchers]
    NotifyFollowers --> ReturnSuccess[Return Created Opportunity]
    ReturnSuccess --> RedirectToDetail[Redirect to<br/>Opportunity Detail Page]

    RedirectToExisting --> End([End])
    RedirectToDetail --> End

    style Start fill:#e1f5ff
    style CreateOpp fill:#c8e6c9
    style ShowDuplicates fill:#fff9c4
    style ReturnError fill:#ffcdd2
```

---

## 3. PAYMENT GATEWAY INTEGRATION (STRIPE)

### 3.1 Subscription Checkout Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Stripe
    participant Webhook
    participant Database

    User->>Frontend: Click "Subscribe to Pro"
    Frontend->>Frontend: Check if logged in

    alt Not Logged In
        Frontend->>User: Redirect to Sign In
        User->>Frontend: Complete Sign In
    end

    Frontend->>Backend: POST /api/v1/subscriptions/checkout<br/>{tier: "pro", success_url, cancel_url}

    Backend->>Database: Get or Create User
    Backend->>Database: Check Existing Subscription

    Backend->>Stripe: Check/Create Stripe Customer<br/>stripe.Customer.create()
    Stripe-->>Backend: customer_id

    Backend->>Database: Store stripe_customer_id

    Backend->>Stripe: Create Checkout Session<br/>stripe.checkout.Session.create({<br/>  customer: customer_id,<br/>  mode: "subscription",<br/>  line_items: [{price: STRIPE_PRICE_PRO}],<br/>  success_url, cancel_url<br/>})

    Stripe-->>Backend: session object with URL
    Backend-->>Frontend: {checkout_url: session.url}

    Frontend->>User: Redirect to Stripe Checkout
    User->>Stripe: Enter Payment Details<br/>(Card Number, CVC, Expiry)

    alt Payment Declined
        Stripe->>User: Show Error: "Card Declined"
        User->>Stripe: Try Different Card
    end

    alt 3D Secure Required
        Stripe->>User: Prompt 3D Secure Authentication
        User->>Stripe: Complete 3DS Verification
    end

    Stripe->>Stripe: Process Payment
    Stripe->>User: Redirect to success_url

    Stripe->>Webhook: POST /api/v1/webhook/stripe<br/>Event: checkout.session.completed

    Webhook->>Webhook: Verify Signature<br/>stripe.Webhook.construct_event()

    Webhook->>Stripe: Retrieve Session Details<br/>stripe.checkout.Session.retrieve(session_id)
    Stripe-->>Webhook: session object with subscription_id

    Webhook->>Database: Find User by stripe_customer_id
    Webhook->>Database: UPDATE subscriptions SET<br/>stripe_subscription_id = subscription_id,<br/>tier = "PRO",<br/>status = "ACTIVE",<br/>current_period_start = now,<br/>current_period_end = now + 30 days

    Webhook-->>Stripe: 200 OK

    User->>Frontend: Lands on account.html?checkout=success
    Frontend->>Backend: GET /api/v1/users/me
    Backend->>Database: Query User with Subscription
    Database-->>Backend: User with tier="PRO"
    Backend-->>Frontend: User data
    Frontend->>User: Show Success Message<br/>"Welcome to Pro! 🎉"

    Note over User,Database: User now has unlimited access to Pro features
```

### 3.2 Pay-Per-Unlock Flow (One-Time Payment)

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant StripeJS
    participant Stripe
    participant Database

    User->>Frontend: Click "Unlock This Opportunity" ($15)
    Frontend->>Frontend: Check Authentication
    Frontend->>Backend: GET /api/v1/users/me
    Backend-->>Frontend: User data (tier: "FREE")

    Frontend->>Backend: POST /api/v1/subscriptions/pay-per-unlock<br/>{opportunity_id: 123}

    Backend->>Database: Check if Already Unlocked

    alt Already Unlocked
        Backend-->>Frontend: {error: "Already unlocked"}
        Frontend->>User: Show: "You already have access"
    else Not Unlocked
        Backend->>Stripe: Create PaymentIntent<br/>stripe.PaymentIntent.create({<br/>  amount: 1500,<br/>  currency: "usd",<br/>  metadata: {<br/>    user_id, opportunity_id,<br/>    unlock_type: "pay_per_unlock"<br/>  }<br/>})

        Stripe-->>Backend: {client_secret: "pi_xxx_secret_xxx"}
        Backend-->>Frontend: {client_secret}

        Frontend->>Frontend: Show Payment Modal<br/>with Stripe Elements
        Frontend->>StripeJS: stripe.confirmCardPayment(<br/>  client_secret,<br/>  {payment_method: {card: cardElement}}<br/>)

        StripeJS->>Stripe: Process Payment

        alt Payment Failed
            Stripe-->>StripeJS: {error: "Card declined"}
            StripeJS-->>Frontend: Payment Error
            Frontend->>User: Show Error: "Payment Failed"
        else Payment Succeeded
            Stripe-->>StripeJS: {paymentIntent: {status: "succeeded"}}
            StripeJS-->>Frontend: Payment Success

            Frontend->>Backend: POST /api/v1/subscriptions/confirm-pay-per-unlock<br/>{payment_intent_id}

            Backend->>Stripe: Verify Payment<br/>stripe.PaymentIntent.retrieve(payment_intent_id)
            Stripe-->>Backend: paymentIntent (status: "succeeded")

            Backend->>Database: INSERT INTO unlocked_opportunities<br/>(user_id, opportunity_id,<br/>unlock_method: "PAY_PER_UNLOCK",<br/>amount_paid: 1500,<br/>stripe_payment_intent_id,<br/>unlocked_at: NOW(),<br/>expires_at: NOW() + 30 days)

            Backend->>Database: UPDATE usage_records<br/>unlocked_opportunities += 1

            Backend-->>Frontend: {success: true, expires_at}
            Frontend->>User: Show Success + Unlock Content
            Frontend->>Frontend: Display Premium Content<br/>(Contact Info, Solution Details)
        end
    end

    Note over User,Database: Access expires after 30 days
```

### 3.3 Stripe Webhook Events Handler

```mermaid
flowchart TD
    StripeEvent([Stripe Event Triggered]) --> WebhookEndpoint[POST /api/v1/webhook/stripe]

    WebhookEndpoint --> VerifySignature{Verify Webhook<br/>Signature}

    VerifySignature -->|Invalid| Return401[Return 401 Unauthorized<br/>Log Security Alert]
    VerifySignature -->|Valid| ParseEvent[Parse Event Type]

    ParseEvent --> EventType{Event Type}

    EventType -->|checkout.session.completed| HandleCheckout[Handle Checkout Completed]
    EventType -->|customer.subscription.updated| HandleUpdate[Handle Subscription Updated]
    EventType -->|customer.subscription.deleted| HandleDelete[Handle Subscription Deleted]
    EventType -->|invoice.payment_failed| HandleFailed[Handle Payment Failed]
    EventType -->|invoice.payment_succeeded| HandleSuccess[Handle Payment Succeeded]
    EventType -->|customer.subscription.trial_will_end| HandleTrialEnd[Handle Trial Ending]
    EventType -->|Other| LogEvent[Log Event & Ignore]

    HandleCheckout --> ExtractSession[Extract Session Data:<br/>customer_id,<br/>subscription_id,<br/>metadata]
    ExtractSession --> FindUser[Find User by<br/>stripe_customer_id]
    FindUser --> LinkSubscription[Link Stripe Subscription<br/>to User Record]
    LinkSubscription --> UpdateTier[Update User Tier<br/>based on price_id]
    UpdateTier --> SetActive[Set Status: ACTIVE<br/>Set Period Dates]

    HandleUpdate --> ExtractSub[Extract Subscription Data]
    ExtractSub --> FindSubRecord[Find Subscription Record<br/>by stripe_subscription_id]
    FindSubRecord --> SyncChanges[Sync Changes:<br/>- Status<br/>- Tier (if price changed)<br/>- Period Dates<br/>- cancel_at_period_end]
    SyncChanges --> CheckCancellation{cancel_at_period_end?}
    CheckCancellation -->|Yes| NotifyUser[Send Cancellation Notice]
    CheckCancellation -->|No| UpdateDB[Update Database]

    HandleDelete --> FindDeleteSub[Find Subscription<br/>by stripe_subscription_id]
    FindDeleteSub --> ResetToFree[Reset User to FREE Tier]
    ResetToFree --> SetCanceled[Set Status: CANCELED]
    SetCanceled --> RevokeAccess[Revoke Premium Access]
    RevokeAccess --> EmailCancellation[Send Cancellation Email]

    HandleFailed --> FindFailedSub[Find Subscription<br/>by stripe_subscription_id]
    FindFailedSub --> SetPastDue[Set Status: PAST_DUE]
    SetPastDue --> SendWarning[Send Payment Failed Email<br/>"Update your payment method"]
    SendWarning --> RetrySchedule[Stripe Auto-Retry<br/>Payment (4 attempts)]

    HandleSuccess --> FindSuccessSub[Find Subscription]
    FindSuccessSub --> ConfirmActive[Confirm Status: ACTIVE]
    ConfirmActive --> UpdatePeriod[Update Period Dates<br/>for Next Billing Cycle]
    UpdatePeriod --> SendReceipt[Send Payment Receipt Email]

    HandleTrialEnd --> FindTrialSub[Find Subscription]
    FindTrialSub --> SendTrialReminder[Send Trial Ending Email<br/>"Your trial ends in 3 days"]

    SetActive --> Return200[Return 200 OK to Stripe]
    UpdateDB --> Return200
    NotifyUser --> Return200
    EmailCancellation --> Return200
    SendReceipt --> Return200
    SendTrialReminder --> Return200
    LogEvent --> Return200
    Return401 --> End([End])
    Return200 --> End

    style StripeEvent fill:#fff9c4
    style Return200 fill:#c8e6c9
    style Return401 fill:#ffcdd2
    style HandleCheckout fill:#e1f5ff
    style HandleUpdate fill:#e1f5ff
    style HandleDelete fill:#ffebee
    style HandleFailed fill:#fff3e0
```

### 3.4 Subscription Management & Billing Portal

```mermaid
flowchart TD
    Start([User in Account Settings]) --> ViewSub[View Subscription Info<br/>account.html]

    ViewSub --> SubDetails[Display:<br/>- Current Tier<br/>- Billing Cycle<br/>- Next Payment Date<br/>- Payment Method]

    SubDetails --> UserAction{User Action}

    UserAction -->|Manage Billing| ClickPortal[Click "Manage Billing"]
    UserAction -->|Cancel Subscription| ClickCancel[Click "Cancel Subscription"]
    UserAction -->|Upgrade| ClickUpgrade[Click "Upgrade to Business"]

    ClickPortal --> CreatePortalSession[POST /api/v1/subscriptions/portal]
    CreatePortalSession --> StripePortal[stripe.billing_portal.Session.create{<br/>  customer: stripe_customer_id,<br/>  return_url: account.html<br/>}]
    StripePortal --> RedirectPortal[Redirect to Stripe Portal]

    RedirectPortal --> PortalActions[Stripe Billing Portal:<br/>- Update Payment Method<br/>- View Invoices<br/>- Download Receipts<br/>- Update Billing Info<br/>- Cancel Subscription]

    PortalActions --> PortalChange{Made Changes?}
    PortalChange -->|Yes| TriggerWebhook[Trigger Webhook:<br/>customer.subscription.updated]
    PortalChange -->|No| ReturnToApp[Return to App]

    TriggerWebhook --> SyncChanges[Sync Changes to Database]
    SyncChanges --> ReturnToApp

    ClickCancel --> ConfirmCancel{Confirm Cancellation?}
    ConfirmCancel -->|No| ViewSub
    ConfirmCancel -->|Yes| CancelRequest[POST /api/v1/subscriptions/cancel]

    CancelRequest --> StripeCancelAPI[stripe.Subscription.modify{<br/>  cancel_at_period_end: true<br/>}]

    StripeCancelAPI --> UpdateDB[Update Database:<br/>cancel_at_period_end = true]
    UpdateDB --> SendEmail[Send Cancellation Email:<br/>"Access until {end_date}"]
    SendEmail --> ShowMessage[Show: "Subscription will cancel<br/>at end of billing period"]
    ShowMessage --> ViewSub

    ClickUpgrade --> CheckoutFlow[Redirect to Checkout<br/>with Business tier]
    CheckoutFlow --> NewCheckout[POST /api/v1/subscriptions/checkout<br/>{tier: "business"}]
    NewCheckout --> StripeCheckout[Create Checkout Session<br/>with Proration]
    StripeCheckout --> CompleteUpgrade[Complete Payment]
    CompleteUpgrade --> WebhookUpdate[Webhook Updates Tier]
    WebhookUpdate --> ReturnToApp

    ReturnToApp --> End([End])

    style Start fill:#e1f5ff
    style PortalActions fill:#fff9c4
    style ShowMessage fill:#c8e6c9
```

### 3.5 Payment Pricing Structure

```mermaid
graph LR
    subgraph "Pricing Tiers"
        Free[FREE - $0/month<br/>✓ 10 opportunity views/month<br/>✓ 0 unlocks<br/>✓ Browse & validate<br/>✓ Limited submissions]

        Pro[PRO - $99/month<br/>✓ Unlimited views<br/>✓ Unlimited unlocks<br/>✓ Full access<br/>✓ Priority support<br/>✓ Advanced analytics]

        Business[BUSINESS - $499/month<br/>✓ Everything in Pro<br/>✓ API access<br/>✓ Team features<br/>✓ Custom analytics<br/>✓ Dedicated support]

        Enterprise[ENTERPRISE - Custom<br/>✓ Everything in Business<br/>✓ Custom features<br/>✓ SLA guarantees<br/>✓ White-label option<br/>✓ Dedicated account manager]
    end

    subgraph "One-Time Options"
        PayPerUnlock[Pay-Per-Unlock<br/>$15.00 per opportunity<br/>✓ 30-day access<br/>✓ Premium content<br/>✓ Contact information]

        IdeaValidation[Idea Validation Service<br/>$9.99 per validation<br/>✓ AI-powered analysis<br/>✓ Market assessment<br/>✓ Feasibility report]
    end

    Free -->|Upgrade| Pro
    Pro -->|Upgrade| Business
    Business -->|Upgrade| Enterprise

    Free -.->|Alternative| PayPerUnlock
    Free -.->|Additional| IdeaValidation

    style Free fill:#e3f2fd
    style Pro fill:#c8e6c9
    style Business fill:#fff9c4
    style Enterprise fill:#f3e5f5
    style PayPerUnlock fill:#ffe0b2
    style IdeaValidation fill:#ffe0b2
```

---

## 4. TECHNICAL COMPONENTS & DATA FLOW

### 4.1 Database Schema & Relationships

```mermaid
erDiagram
    USER ||--o{ OPPORTUNITY : creates
    USER ||--o{ VALIDATION : makes
    USER ||--o{ COMMENT : posts
    USER ||--o{ WATCHLIST_ITEM : saves
    USER ||--|| SUBSCRIPTION : has
    USER ||--o{ USAGE_RECORD : tracks
    USER ||--o{ NOTIFICATION : receives
    USER ||--o{ UNLOCKED_OPPORTUNITY : unlocks

    OPPORTUNITY ||--o{ VALIDATION : receives
    OPPORTUNITY ||--o{ COMMENT : has
    OPPORTUNITY ||--o{ WATCHLIST_ITEM : in
    OPPORTUNITY ||--o{ UNLOCKED_OPPORTUNITY : unlocked_by
    OPPORTUNITY ||--o{ OPPORTUNITY : "duplicates (self-ref)"

    SUBSCRIPTION ||--o{ UNLOCKED_OPPORTUNITY : "provides access"

    USER {
        int id PK
        string email UK
        string hashed_password
        string name
        string oauth_provider
        string oauth_id
        int impact_points
        boolean is_verified
        boolean is_admin
        string otp_secret
        boolean otp_enabled
        timestamp created_at
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

    UNLOCKED_OPPORTUNITY {
        int id PK
        int user_id FK
        int opportunity_id FK
        string unlock_method
        int amount_paid
        string stripe_payment_intent_id
        timestamp unlocked_at
        timestamp expires_at
    }

    VALIDATION {
        int id PK
        int user_id FK
        int opportunity_id FK
        timestamp created_at
    }

    COMMENT {
        int id PK
        int user_id FK
        int opportunity_id FK
        text content
        int likes
        timestamp created_at
    }

    WATCHLIST_ITEM {
        int id PK
        int user_id FK
        int opportunity_id FK
        timestamp added_at
    }

    USAGE_RECORD {
        int id PK
        int user_id FK
        timestamp period_start
        timestamp period_end
        int opportunity_views
        int unlocked_opportunities
        int csv_exports
    }

    NOTIFICATION {
        int id PK
        int user_id FK
        string type
        string title
        text message
        boolean read
        timestamp created_at
    }
```

### 4.2 API Request Flow with Authentication

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant ProxyServer
    participant FastAPI
    participant AuthMiddleware
    participant Router
    participant Service
    participant Database
    participant ExternalAPI

    User->>Browser: Interact with UI
    Browser->>Browser: Check localStorage for JWT

    alt No JWT Token
        Browser->>User: Redirect to /signin.html
    else Has JWT Token
        Browser->>ProxyServer: HTTP Request<br/>GET /api/v1/opportunities<br/>Authorization: Bearer {JWT}

        ProxyServer->>FastAPI: Forward to Backend<br/>(Port 8000)

        FastAPI->>AuthMiddleware: CORS Check
        AuthMiddleware->>AuthMiddleware: Validate Origin

        AuthMiddleware->>Router: Route to opportunities.py
        Router->>Router: Dependency Injection:<br/>get_current_active_user()

        Router->>AuthMiddleware: Decode & Verify JWT
        AuthMiddleware->>AuthMiddleware: Check Signature<br/>Check Expiration

        alt JWT Invalid/Expired
            AuthMiddleware-->>Browser: 401 Unauthorized
            Browser->>User: Redirect to Sign In
        else JWT Valid
            AuthMiddleware->>Database: Query User by user_id<br/>from JWT payload
            Database-->>AuthMiddleware: User Record

            AuthMiddleware->>Router: Inject current_user

            Router->>Service: Call Business Logic<br/>get_opportunities(filters)

            Service->>Database: SELECT opportunities<br/>JOIN validations<br/>WHERE filters
            Database-->>Service: Opportunity Records

            Service->>Service: Apply Tier-Based Filtering<br/>Check Usage Limits

            alt Premium Content & Free Tier
                Service->>Database: Check unlocked_opportunities
                Database-->>Service: Unlock Status
                Service->>Service: Mask Premium Fields
            end

            Service-->>Router: Processed Data
            Router-->>FastAPI: Response Object

            FastAPI->>FastAPI: Serialize to JSON<br/>Apply Response Model

            FastAPI-->>ProxyServer: JSON Response
            ProxyServer-->>Browser: HTTP 200 OK<br/>{opportunities: [...]}

            Browser->>Browser: Update DOM
            Browser->>User: Display Opportunities
        end
    end

    Note over User,ExternalAPI: Secure JWT-based Authentication Flow
```

### 4.3 Frontend-Backend Communication Flow

```mermaid
flowchart LR
    subgraph "Frontend - Port 5000"
        HTML[HTML Pages]
        AppJS[app.js<br/>Application Logic]
        APIJS[api.js<br/>OppGridAPI Class]
        AuthJS[auth.js<br/>Token Management]
        LocalStorage[(localStorage)]
    end

    subgraph "Network Layer"
        FetchAPI[Fetch API<br/>HTTP/HTTPS]
        CORS[CORS Headers]
    end

    subgraph "Backend - Port 8000"
        FastAPIApp[FastAPI Application]
        Middleware[Middleware Stack]
        RouterLayer[Router Layer]
        ServiceLayer[Service Layer]
        ModelLayer[Model Layer]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis Cache<br/>Optional)]
    end

    subgraph "External APIs"
        Stripe[Stripe API]
        EmailAPI[Resend Email]
        OAuth[OAuth Providers]
    end

    HTML --> AppJS
    AppJS --> APIJS
    AppJS --> AuthJS
    AuthJS --> LocalStorage
    LocalStorage -.->|JWT Token| AuthJS

    APIJS -->|HTTP Requests| FetchAPI
    FetchAPI --> CORS
    CORS --> FastAPIApp

    FastAPIApp --> Middleware
    Middleware -->|Route Matching| RouterLayer
    RouterLayer -->|Business Logic| ServiceLayer
    ServiceLayer -->|ORM Queries| ModelLayer
    ModelLayer -->|SQL| PostgreSQL
    ModelLayer -.->|Cache| Redis

    ServiceLayer -->|External Calls| Stripe
    ServiceLayer -->|Send Emails| EmailAPI
    RouterLayer -->|OAuth Flow| OAuth

    PostgreSQL -->|Results| ModelLayer
    ModelLayer -->|Pydantic Models| ServiceLayer
    ServiceLayer -->|Response| RouterLayer
    RouterLayer -->|JSON| FastAPIApp
    FastAPIApp --> CORS
    CORS --> FetchAPI
    FetchAPI -->|Response Data| APIJS
    APIJS -->|Data| AppJS
    AppJS -->|Update UI| HTML

    style LocalStorage fill:#ffe0b2
    style PostgreSQL fill:#ffebee
    style FastAPIApp fill:#c8e6c9
    style FetchAPI fill:#e1f5ff
```

### 4.4 Real-Time Data Flow - Opportunity Validation

```mermaid
flowchart TD
    UserClick([User Clicks<br/>"I Need This Too"]) --> JSHandler[JavaScript Event Handler]

    JSHandler --> CheckToken{JWT Token<br/>Exists?}
    CheckToken -->|No| RedirectLogin[Redirect to /signin.html]
    CheckToken -->|Yes| PrepareRequest[Prepare API Request]

    PrepareRequest --> APICall[POST /api/v1/validations/<br/>Headers: Authorization Bearer<br/>Body: {opportunity_id: 123}]

    APICall --> ProxyRoute[Proxy Routes to Backend]
    ProxyRoute --> FastAPIEndpoint[FastAPI Router:<br/>validations.py]

    FastAPIEndpoint --> AuthDep[Dependency:<br/>get_current_active_user]
    AuthDep --> DecodeJWT[Decode JWT Token]
    DecodeJWT --> ValidToken{Token Valid?}

    ValidToken -->|No| Return401[Return 401 Unauthorized]
    ValidToken -->|Yes| QueryUser[Query User from Database]

    QueryUser --> CheckExisting[Check if User Already<br/>Validated This Opportunity]
    CheckExisting --> AlreadyValidated{Already<br/>Validated?}

    AlreadyValidated -->|Yes| Return400[Return 400 Bad Request<br/>"Already validated"]
    AlreadyValidated -->|No| CreateValidation[INSERT INTO validations<br/>(user_id, opportunity_id)]

    CreateValidation --> UpdateCount[UPDATE opportunities<br/>SET validation_count =<br/>validation_count + 1<br/>WHERE id = 123]

    UpdateCount --> RecalcFeasibility[Recalculate<br/>Feasibility Score]
    RecalcFeasibility --> Formula[Formula:<br/>base_severity × log1+validation_count<br/>× geographic_multiplier]

    Formula --> UpdateScore[UPDATE opportunities<br/>SET feasibility_score]

    UpdateScore --> CheckMilestone{Validation Count<br/>Milestone?}
    CheckMilestone -->|10, 50, 100, etc.| NotifyAuthor[Create Notification<br/>for Opportunity Author]
    CheckMilestone -->|No| UpdateImpact[UPDATE users<br/>SET impact_points += 10]

    NotifyAuthor --> UpdateImpact
    UpdateImpact --> CommitTx[COMMIT Transaction]

    CommitTx --> ReturnSuccess[Return 201 Created<br/>{validation_id, new_count,<br/>new_feasibility_score}]

    ReturnSuccess --> UpdateFrontend[Update Frontend UI]
    UpdateFrontend --> ChangeButton[Change Button:<br/>"I Need This Too" →<br/>"Validated ✓"]
    ChangeButton --> UpdateBadge[Update Validation Count<br/>Display]
    UpdateBadge --> UpdateScore2[Update Feasibility<br/>Score Badge]
    UpdateScore2 --> AnimateChange[Animate Counter<br/>Increment]

    AnimateChange --> End([Complete])
    Return401 --> ShowError[Show Error Message]
    Return400 --> ShowError
    ShowError --> End
    RedirectLogin --> End

    style UserClick fill:#e1f5ff
    style CreateValidation fill:#c8e6c9
    style Return401 fill:#ffcdd2
    style Return400 fill:#ffcdd2
    style AnimateChange fill:#fff9c4
```

### 4.5 Deployment Architecture (Replit)

```mermaid
graph TB
    subgraph "Replit Platform"
        subgraph "Repl Container"
            ServerPy[server.py<br/>Main Process]

            subgraph "Thread 1"
                FrontendServer[HTTP Server<br/>Port $PORT 5000<br/>SimpleHTTPRequestHandler]
            end

            subgraph "Thread 2"
                BackendServer[Uvicorn Server<br/>Port 8000<br/>FastAPI App]
            end

            ServerPy -->|Start Thread 1| FrontendServer
            ServerPy -->|Start Thread 2| BackendServer
            ServerPy -->|Health Check| BackendServer
        end

        subgraph "Replit Database"
            ReplitPostgres[(PostgreSQL<br/>Managed Database)]
        end

        subgraph "Replit Storage"
            FileSystem[File System<br/>Static Files<br/>HTML/CSS/JS]
        end

        subgraph "Environment"
            Secrets[Secrets/Environment Variables<br/>STRIPE_SECRET_KEY<br/>DATABASE_URL<br/>SECRET_KEY<br/>OAUTH_CREDENTIALS]
        end
    end

    subgraph "External Network"
        Internet([Internet])
        ReplitDomain[Replit Domain<br/>https://project-name.repl.co]
        CustomDomain[Custom Domain<br/>https://friction.app]
    end

    subgraph "External Services"
        StripeServers[Stripe Servers]
        GoogleAPI[Google OAuth]
        GitHubAPI[GitHub OAuth]
        EmailProvider[Resend Email API]
    end

    Internet --> ReplitDomain
    Internet --> CustomDomain
    ReplitDomain --> FrontendServer
    CustomDomain --> FrontendServer

    FrontendServer -->|Serve Static| FileSystem
    FrontendServer -->|Proxy /api/*| BackendServer

    BackendServer -->|Read Secrets| Secrets
    BackendServer -->|SQL Queries| ReplitPostgres

    BackendServer -->|API Calls| StripeServers
    BackendServer -->|OAuth| GoogleAPI
    BackendServer -->|OAuth| GitHubAPI
    BackendServer -->|Send Emails| EmailProvider

    StripeServers -->|Webhooks| BackendServer

    style FrontendServer fill:#e1f5ff
    style BackendServer fill:#c8e6c9
    style ReplitPostgres fill:#ffebee
    style Secrets fill:#fff9c4
    style StripeServers fill:#ffe0b2
```

---

## 5. SECURITY & DATA PROTECTION

### 5.1 Security Layers

```mermaid
flowchart TD
    Request([Incoming Request]) --> HTTPS{HTTPS?}
    HTTPS -->|No| Reject[Reject - Force HTTPS]
    HTTPS -->|Yes| CORS[CORS Validation]

    CORS --> Origin{Valid Origin?}
    Origin -->|No| Block[Block - 403 Forbidden]
    Origin -->|Yes| RateLimit[Rate Limiting]

    RateLimit --> CheckRate{Within Limits?}
    CheckRate -->|No| Throttle[Return 429 Too Many Requests]
    CheckRate -->|Yes| AuthCheck{Requires Auth?}

    AuthCheck -->|No| PublicEndpoint[Public Endpoint]
    AuthCheck -->|Yes| JWTValidation[JWT Validation]

    JWTValidation --> ValidJWT{Valid Token?}
    ValidJWT -->|No| Unauthorized[Return 401 Unauthorized]
    ValidJWT -->|Yes| UserActive{User Active<br/>& Not Banned?}

    UserActive -->|No| Forbidden[Return 403 Forbidden]
    UserActive -->|Yes| TierCheck[Check Subscription Tier]

    TierCheck --> HasAccess{Has Access<br/>to Feature?}
    HasAccess -->|No| UpgradeRequired[Return 402 Payment Required]
    HasAccess -->|Yes| InputValidation[Input Validation]

    InputValidation --> ValidInput{Valid Input?}
    ValidInput -->|No| BadRequest[Return 400 Bad Request]
    ValidInput -->|Yes| SQLInjection[SQL Injection Protection<br/>ORM Parameterization]

    SQLInjection --> XSSProtection[XSS Protection<br/>Input Sanitization]
    XSSProtection --> CSRFCheck[CSRF Token Check<br/>for State-Changing Ops]

    CSRFCheck --> ProcessRequest[Process Request]
    ProcessRequest --> EncryptData[Encrypt Sensitive Data]

    EncryptData --> DatabaseQuery[Database Query<br/>Encrypted Connection]
    DatabaseQuery --> AuditLog[Audit Log Entry]

    AuditLog --> Response[Generate Response]
    Response --> SanitizeOutput[Sanitize Output<br/>Remove Sensitive Data]

    SanitizeOutput --> SecureHeaders[Add Security Headers:<br/>- X-Content-Type-Options<br/>- X-Frame-Options<br/>- Strict-Transport-Security]

    SecureHeaders --> Success[Return Response]

    PublicEndpoint --> ProcessRequest

    Reject --> End([End])
    Block --> End
    Throttle --> End
    Unauthorized --> End
    Forbidden --> End
    UpgradeRequired --> End
    BadRequest --> End
    Success --> End

    style Request fill:#e1f5ff
    style Success fill:#c8e6c9
    style Reject fill:#ffcdd2
    style Block fill:#ffcdd2
    style Unauthorized fill:#ffcdd2
    style Forbidden fill:#ffcdd2
    style EncryptData fill:#fff9c4
```

### 5.2 Payment Data Security

```mermaid
flowchart LR
    subgraph "Client Side"
        Browser[User Browser]
        StripeJS[Stripe.js SDK]
        NoCardData[❌ No Card Data<br/>Stored Locally]
    end

    subgraph "Application Backend"
        Backend[FastAPI Backend]
        NoCardStorage[❌ Never Store<br/>Card Numbers]
        TokenOnly[✓ Store Only:<br/>- stripe_customer_id<br/>- stripe_subscription_id<br/>- stripe_payment_intent_id]
    end

    subgraph "Stripe Secure Environment"
        StripeAPI[Stripe API]
        PCICompliant[✓ PCI DSS Level 1<br/>Compliant]
        CardVault[Encrypted Card Vault]
        TokenService[Tokenization Service]
    end

    subgraph "Database"
        PostgreSQL[(PostgreSQL)]
        EncryptedFields[✓ Encrypted Fields<br/>✓ No Sensitive Payment Data<br/>✓ Only Reference IDs]
    end

    Browser -->|Card Details| StripeJS
    StripeJS -->|HTTPS Only<br/>Direct to Stripe| StripeAPI
    StripeAPI -->|Store Securely| CardVault
    StripeAPI -->|Generate| TokenService
    TokenService -->|Payment Token| StripeJS
    StripeJS -->|Token Only| Browser
    Browser -->|Token| Backend
    Backend -->|Reference IDs Only| PostgreSQL
    Backend -->|API Calls with Token| StripeAPI

    NoCardData -.->|Never Touches| Browser
    NoCardStorage -.->|Never Touches| Backend

    style StripeAPI fill:#c8e6c9
    style PCICompliant fill:#c8e6c9
    style NoCardData fill:#ffcdd2
    style NoCardStorage fill:#ffcdd2
    style TokenOnly fill:#e1f5ff
```

---

## 6. KEY FEATURES SUMMARY

### Feature Access Matrix

| Feature | Free | Pro | Business | Enterprise |
|---------|------|-----|----------|------------|
| Browse Opportunities | ✓ (10/month) | ✓ Unlimited | ✓ Unlimited | ✓ Unlimited |
| Validate Problems | ✓ | ✓ | ✓ | ✓ |
| Submit Problems | ✓ Limited | ✓ Unlimited | ✓ Unlimited | ✓ Unlimited |
| Comment & Discuss | ✓ | ✓ | ✓ | ✓ |
| Unlock Premium Content | Pay $15 each | ✓ Unlimited | ✓ Unlimited | ✓ Unlimited |
| Advanced Analytics | ✗ | ✓ | ✓ | ✓ |
| AI Validation Service | $9.99 each | $9.99 each | Included | Included |
| API Access | ✗ | ✗ | ✓ | ✓ |
| Team Features | ✗ | ✗ | ✓ | ✓ |
| Priority Support | ✗ | ✓ | ✓ | ✓ Dedicated |
| Custom Features | ✗ | ✗ | ✗ | ✓ |

---

## 7. ENVIRONMENT VARIABLES REQUIRED

```bash
# Application
SECRET_KEY=<random-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:pass@host:port/database
# Or Replit Managed:
REPLIT_DB_URL=<auto-provided>

# Stripe Payment
STRIPE_SECRET_KEY=sk_live_xxx  # or sk_test_xxx for testing
STRIPE_PUBLISHABLE_KEY=pk_live_xxx  # or pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_PRO=price_xxx  # Price ID for Pro tier
STRIPE_PRICE_BUSINESS=price_xxx  # Price ID for Business tier

# OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx

# Email (Optional)
RESEND_API_KEY=re_xxx
FROM_EMAIL=noreply@friction.app

# Frontend URL
FRONTEND_URL=https://friction.repl.co  # or custom domain

# Optional
ENVIRONMENT=production  # or development
LOG_LEVEL=INFO
```

---

## 8. API ENDPOINTS REFERENCE

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - Email/password login
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/verify-email` - Verify email address
- `POST /api/v1/auth/request-reset` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password
- `GET /api/v1/oauth/google` - Google OAuth login
- `GET /api/v1/oauth/github` - GitHub OAuth login

### Opportunity Endpoints
- `GET /api/v1/opportunities/` - List opportunities (with filters)
- `GET /api/v1/opportunities/{id}` - Get single opportunity
- `POST /api/v1/opportunities/` - Create opportunity
- `PUT /api/v1/opportunities/{id}` - Update opportunity
- `DELETE /api/v1/opportunities/{id}` - Delete opportunity
- `GET /api/v1/opportunities/search` - Full-text search

### Validation Endpoints
- `POST /api/v1/validations/` - Validate opportunity
- `DELETE /api/v1/validations/{id}` - Remove validation

### Payment & Subscription Endpoints
- `GET /api/v1/subscriptions/stripe-key` - Get publishable key
- `POST /api/v1/subscriptions/checkout` - Create checkout session
- `POST /api/v1/subscriptions/portal` - Create billing portal session
- `POST /api/v1/subscriptions/cancel` - Cancel subscription
- `POST /api/v1/subscriptions/pay-per-unlock` - Create payment intent
- `POST /api/v1/subscriptions/confirm-pay-per-unlock` - Confirm unlock payment
- `POST /api/v1/subscriptions/unlock` - Unlock with subscription
- `POST /api/v1/webhook/stripe` - Stripe webhook handler (canonical)

### Analytics Endpoints
- `GET /api/v1/analytics/opportunities` - Opportunity statistics
- `GET /api/v1/analytics/feasibility` - Feasibility analysis
- `GET /api/v1/analytics/geographic` - Geographic distribution
- `GET /api/v1/analytics/top-feasible` - Top feasible opportunities

### User Endpoints
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{id}/profile` - Get user profile
- `GET /api/v1/users/{id}/stats` - Get user statistics

---

## File Locations

**Frontend:**
- HTML Pages: `/index.html`, `/signin.html`, `/signup.html`, `/pricing.html`, etc.
- JavaScript: `/js/app.js`, `/js/api.js`, `/js/auth.js`, `/js/config.js`
- Styles: `/css/styles.css`

**Backend:**
- Main App: `/backend/app/main.py`
- Routers: `/backend/app/routers/*.py`
- Models: `/backend/app/models/*.py`
- Services: `/backend/app/services/*.py`
- Core: `/backend/app/core/*.py`

**Server:**
- Entry Point: `/server.py`

**Database:**
- Init Script: `/backend/init_db.py`

---

## Technology Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | Vanilla JavaScript, HTML5, CSS3, Stripe.js |
| Backend | Python 3.8+, FastAPI, Uvicorn |
| Database | PostgreSQL (Replit Managed) |
| ORM | SQLAlchemy 2.0 |
| Authentication | JWT (python-jose), OAuth2 (authlib) |
| Payment | Stripe SDK v8.5 |
| Email | Resend API |
| Hosting | Replit (Container + PostgreSQL) |
| Security | bcrypt, HTTPS, CORS, Rate Limiting |

---

**Document Version:** 1.0
**Last Updated:** 2024-01-XX
**Application:** Friction (OppGrid API)
