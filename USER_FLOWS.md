# Project-Spark User Flows Documentation

## Core User Flows

## Opportunity Access Model (Canonical)

OppGrid uses a **time-decay access model**. The backend returns entitlement info (e.g., `content_state`) for each opportunity, and the UI should render CTAs based on that state.

**Time windows (days since discovered/created):**
- **HOT**: 0–7 days
- **FRESH**: 8–30 days
- **VALIDATED**: 31–90 days
- **ARCHIVE**: 91+ days

**Common entitlement states (example):**
- `full`: show all content available to the user
- `preview`: show limited fields + upgrade CTA
- `locked`: show locked state + countdown/unlock info + upgrade CTA
- `pay_per_unlock`: eligible for $15 one-time unlock (ARCHIVE), 30-day access, daily limit 5
- `fast_pass`: eligible for $99 one-time unlock (Business tier, HOT), 30-day access

**One-time unlock expiry:**
- When a one-time unlock is active, the backend includes `unlock_expires_at` so the UI can display “access until …”.

---

### 1. User Registration & Authentication Flow

#### 1A. New User Registration
```
START → Landing Page (index.html)
  ↓
Click "Sign Up" → Signup Page (signup.html)
  ↓
Enter Details:
  - Name
  - Email
  - Password (min 8 chars)
  ↓
Submit Form → POST /api/v1/auth/register
  ↓
[SUCCESS] → Auto-login with JWT token
  ↓
Redirect to Dashboard (index.html)
  ↓
Show Welcome Message
END
```

**Error Handling:**
- Email already exists → Show error "Email already registered"
- Weak password → Show error "Password must be at least 8 characters"
- Network error → Show retry option

#### 1B. User Login
```
START → Landing Page
  ↓
Click "Sign in" → Sign-in Page (signin.html)
  ↓
Enter Credentials:
  - Email
  - Password
  ↓
Submit Form → POST /api/v1/auth/login
  ↓
[SUCCESS] → Receive JWT token
  ↓
Store token in localStorage
  ↓
Redirect to Dashboard
END
```

**Error Handling:**
- Invalid credentials → Show "Invalid email or password"
- Account not verified → (Future) Prompt email verification

#### 1C. Password Reset Flow (If Enabled)
```
START → Sign-in Page
  ↓
Click "Forgot Password?" → Reset Password Page (reset-password.html)
  ↓
Enter Email Address
  ↓
[If enabled] Submit → POST /api/v1/auth/request-reset
  ↓
[MISSING] Send email with reset token
  ↓
[MISSING] User clicks email link
  ↓
[If enabled] Enter new password → POST /api/v1/auth/reset-password
  ↓
Redirect to Sign-in
END
```

---

### 2. Opportunity Discovery & Search Flow

#### 2A. Browse Opportunities (Main Dashboard)
```
START → Dashboard (index.html)
  ↓
Page loads → GET /api/v1/opportunities
  ↓
Display opportunities as cards with:
  - Title, Description
  - Category badge
  - Validation count
  - Feasibility score badge
  - Geographic scope badge
  - Access badge / state (e.g. HOT/FRESH/VALIDATED/ARCHIVE)
  - CTA varies by entitlement (`content_state`): View / Upgrade / Unlock
  ↓
USER ACTIONS:
  ├─ Click card → View full details (modal/detail page)
  ├─ Click "I Need This Too" → Validation Flow (see 3A)
  ├─ Apply filters → Filtered Results Flow (see 2B)
  └─ Search → Search Flow (see 2C)
END
```

#### 2B. Filter Opportunities
```
START → Dashboard with filters visible
  ↓
USER SELECTS FILTERS:
  ├─ Geographic Scope (local/regional/national/international/online)
  ├─ Country (dropdown)
  ├─ Sort (newest/most validated/highest feasibility)
  ├─ Category (from predefined list)
  └─ Completion Status (open/in_progress/solved/abandoned)
  ↓
Apply Filters → GET /api/v1/opportunities?filters
  ↓
Display filtered results
  ↓
Show result count "Showing X opportunities"
END
```

#### 2C. Search Opportunities
```
START → Click search icon/input
  ↓
Navigate to Search Page (search.html)
  ↓
Enter search query
  ↓
Submit → POST /api/v1/opportunities/search
  ↓
Backend searches:
  - Title (weighted)
  - Description
  - Category/Subcategory
  ↓
Display ranked results
  ↓
USER ACTIONS:
  ├─ Click result → View details
  ├─ Refine search → New query
  └─ Clear search → Return to dashboard
END
```

#### 2D. Browse by Category
```
START → Click category filter OR category.html
  ↓
Display category grid with counts
  ↓
Select category → Filter opportunities
  ↓
GET /api/v1/opportunities?category={category}
  ↓
Display category-specific opportunities
END
```

---

### 3. Opportunity Interaction Flows

#### 3A. Validate Opportunity ("I Need This Too")
```
START → Viewing opportunity card/details
  ↓
Click "I Need This Too" button
  ↓
[CHECK] User authenticated?
  ├─ NO → Redirect to sign-in (signin.html?redirect=...)
  └─ YES → Continue
  ↓
POST /api/v1/validations
  - opportunity_id
  - user_id (from JWT)
  ↓
[SUCCESS]
  ↓
Update validation count (+1)
  ↓
Change button to "Validated ✓"
  ↓
Update feasibility score (backend recalculates)
END
```

**Remove Validation:**
```
Click "Validated ✓" button
  ↓
DELETE /api/v1/validations/{validation_id}
  ↓
Update count (-1)
  ↓
Revert button to "I Need This Too"
END
```

#### 3B. Comment on Opportunity
```
START → View opportunity details
  ↓
Scroll to comments section
  ↓
Click "Add Comment"
  ↓
[CHECK] User authenticated?
  ├─ NO → Redirect to sign-in (signin.html?redirect=...)
  └─ YES → Continue
  ↓
Enter comment text
  ↓
Submit → POST /api/v1/comments
  ↓
Display new comment with:
  - User avatar/name
  - Comment content
  - Timestamp
  - Like button
  ↓
Update comment count
END
```

**Like Comment:**
```
Click like button → PUT /api/v1/comments/{id}/like
  ↓
Increment like count
  ↓
Disable button (one like per user)
END
```

#### 3C. Create New Opportunity
```
START → Dashboard
  ↓
Click "Share a Friction" / "Submit Opportunity"
  ↓
[CHECK] User authenticated?
  ├─ NO → Redirect to sign-in (signin.html?redirect=...)
  └─ YES → Continue
  ↓
FORM APPEARS:
  ↓
Enter Details:
  ├─ Title (required)
  ├─ Description (required)
  ├─ Category (dropdown)
  ├─ Subcategory (conditional dropdown)
  ├─ Severity (1-5 scale)
  ├─ Geographic Scope (required)
  ├─ Country (conditional)
  ├─ Region (conditional)
  ├─ City (conditional)
  └─ Anonymous submission? (checkbox)
  ↓
[DUPLICATE DETECTION]
  ↓
Backend checks similarity
  ↓
POST /api/v1/analytics/check-duplicate
  ↓
IF similarity > 50%:
  ├─ Show duplicate warning modal
  ├─ Display top 5 similar opportunities
  ├─ USER CHOICE:
  │   ├─ "Validate Existing" → Validation Flow (3A)
  │   └─ "Submit Anyway" → Continue
  └─ Continue
  ↓
Submit → POST /api/v1/opportunities
  ↓
[SUCCESS]
  ↓
Opportunity created with:
  - Status: "open"
  - Validation count: 1 (auto-validation)
  - Initial feasibility score calculated
  ↓
Redirect to opportunity details
  ↓
Show success message "Opportunity shared!"
END
```

---

### 4. Profile & Settings Management

#### 4A. View Profile
```
START → Dashboard
  ↓
Click user avatar/name → Profile Page (profile.html)
  ↓
[CURRENT STATE - Static]
Display sections:
  ├─ User Info (avatar, name, bio, joined date)
  ├─ Stats (opportunities, validations, impact points)
  ├─ Activity Feed (recent actions)
  ├─ Validated Opportunities (list)
  ├─ Shared Items (user's opportunities)
  └─ Watchlist (saved opportunities)
  ↓
[NEEDED - Dynamic]
GET /api/v1/users/me
  ↓
Fetch real user data
  ↓
GET /api/v1/opportunities?user_id={user_id}
  ↓
Display user's opportunities
END
```

#### 4B. Edit Profile
```
START → Profile Page
  ↓
Click "Edit Profile"
  ↓
Navigate to Settings (settings.html)
  ↓
PROFILE INFORMATION FORM:
  ├─ Name
  ├─ Email (readonly)
  ├─ Bio
  └─ Avatar URL
  ↓
Make changes
  ↓
Click "Save Changes"
  ↓
[CURRENT - Partial]
Form submission handler exists
  ↓
[NEEDED]
PUT /api/v1/users/me
  - name
  - bio
  - avatar_url
  ↓
[SUCCESS]
  ↓
Update localStorage user data
  ↓
Show success toast "Profile updated"
  ↓
Redirect to profile
END
```

#### 4C. Settings Management
```
START → Settings Page (settings.html)
  ↓
TABS AVAILABLE:
  ├─ Profile Information (see 4B)
  ├─ Notification Preferences [UI ONLY]
  ├─ Account Settings [PARTIAL]
  └─ Connected Accounts [UI ONLY]
  ↓
NOTIFICATION PREFERENCES [MISSING]:
  [NEEDED]
  ├─ Email notifications toggle
  ├─ Push notifications toggle
  └─ PUT /api/v1/users/me/preferences
  ↓
ACCOUNT SETTINGS:
  ├─ Change Password [EXISTS]
  │   ├─ Enter current password
  │   ├─ Enter new password
  │   └─ PUT /api/v1/users/me/password
  ├─ Enable 2FA [MISSING]
  ├─ Data Export [MISSING]
  └─ Delete Account [MISSING]
  ↓
CONNECTED ACCOUNTS [MISSING]:
  └─ OAuth providers (Google, GitHub)
END
```

---

### 5. Analytics & Research Dashboard Flow

#### 5A. View Research Dashboard
```
START → Dashboard (index.html)
  ↓
Click "Research Dashboard" tab
  ↓
[CURRENT - Static SVG]
Display placeholder charts
  ↓
[NEEDED - Dynamic]
PARALLEL API CALLS:
  ├─ GET /api/v1/analytics/completion-stats
  ├─ GET /api/v1/analytics/top-feasible
  ├─ GET /api/v1/analytics/geographic/distribution
  └─ GET /api/v1/analytics/feasibility/{id} (for selected opportunity)
  ↓
RENDER INTERACTIVE CHARTS:
  ├─ Validation trends over time
  ├─ Completion status distribution
  ├─ Geographic heatmap
  ├─ Top feasible opportunities list
  └─ Category breakdown
  ↓
USER INTERACTIONS:
  ├─ Click chart segment → Filter dashboard
  ├─ Hover → Show tooltips
  └─ Select date range → Refresh data
END
```

#### 5B. View Feasibility Analysis
```
START → Viewing opportunity
  ↓
Click "View Feasibility Analysis"
  ↓
GET /api/v1/analytics/feasibility/{opportunity_id}
  ↓
Display analysis modal/page:
  ├─ Overall Score (0-100)
  ├─ Score Breakdown:
  │   ├─ Validation Count (0-30 pts)
  │   ├─ Severity (0-20 pts)
  │   ├─ Growth Rate (0-25 pts)
  │   ├─ Problem Age (0-15 pts)
  │   └─ Market Size (0-10 pts)
  ├─ Recommendations (text analysis)
  └─ Action Items
END
```

#### 5C. Browse Top Feasible Opportunities
```
START → Dashboard or Research tab
  ↓
Click "Most Feasible" filter/tab
  ↓
GET /api/v1/analytics/top-feasible?min_score=50&limit=20
  ↓
Display ranked list with:
  - Rank number
  - Opportunity details
  - Feasibility score badge
  - Validation count
  ↓
USER ACTIONS:
  ├─ Click opportunity → View details
  └─ Validate → Validation Flow (3A)
END
```

---

### 6. Geographic Filtering & Discovery

#### 6A. Filter by Geographic Scope
```
START → Dashboard filters
  ↓
Select scope from dropdown:
  ├─ Local
  ├─ Regional
  ├─ National
  ├─ International
  └─ Online
  ↓
GET /api/v1/analytics/geographic/by-scope?scope={scope}
  ↓
Display filtered opportunities
  ↓
Show scope badge on cards
END
```

#### 6B. Filter by Location
```
START → Dashboard filters
  ↓
Enter/select:
  ├─ Country (dropdown)
  ├─ Region (conditional)
  └─ City (conditional)
  ↓
GET /api/v1/analytics/geographic/by-location?country={country}&region={region}&city={city}
  ↓
Display location-specific opportunities
  ↓
Show location badge on cards
END
```

---

### 7. Completion Tracking Flow

#### 7A. Mark Opportunity as In Progress
```
START → Opportunity details
  ↓
[CHECK] User is owner OR has permission
  ↓
Click "Mark as In Progress"
  ↓
PUT /api/v1/opportunities/{id}
  - completion_status: "in_progress"
  ↓
Update status badge
  ↓
Show in "In Progress" filter
END
```

#### 7B. Mark Opportunity as Solved
```
START → Opportunity details (status: "in_progress")
  ↓
Click "Mark as Solved"
  ↓
MODAL APPEARS:
  ↓
Enter solution details:
  ├─ Solution Description (required)
  └─ Solved By (user/organization)
  ↓
Submit → PUT /api/v1/opportunities/{id}
  - completion_status: "solved"
  - solution_description
  - solved_by
  - solved_at (auto-timestamp)
  ↓
Update status badge to "Solved ✓"
  ↓
Display solution description
  ↓
Remove from "Open" filter
  ↓
Add to "Solved" showcase
END
```

---

### 8. User Journey Maps

#### 8A. First-Time User Journey
```
DAY 1: Discovery & Registration
  ↓
Land on site → Browse public opportunities → See value
  ↓
Sign up → Confirm email [MISSING] → Profile setup
  ↓
DAY 1-3: Exploration
  ↓
Validate 3-5 opportunities → Earn first badge [MISSING]
  ↓
Browse by category → Discover pain points
  ↓
DAY 4-7: Engagement
  ↓
Submit first opportunity → Duplicate detection guides user
  ↓
Receive validations → See impact points grow [MISSING]
  ↓
Comment on similar opportunities
  ↓
WEEK 2+: Regular User
  ↓
Check dashboard weekly → Track validated opportunities
  ↓
Use research dashboard → Identify trends
  ↓
Share success stories → Community building
```

#### 8B. Researcher/Analyst Journey
```
START → Research Dashboard
  ↓
Filter by feasibility score → Identify high-potential opportunities
  ↓
Analyze geographic distribution → Market insights
  ↓
Track completion rates → Success metrics
  ↓
Export data [MISSING] → External analysis
  ↓
Share findings → Community feedback
END
```

#### 8C. Entrepreneur Journey
```
START → Browse validated opportunities
  ↓
Filter by feasibility + validation count → Find viable ideas
  ↓
Read comments → Understand pain points
  ↓
Contact validators [MISSING] → Market research
  ↓
Mark as "In Progress" → Build solution
  ↓
Update with progress → Community engagement
  ↓
Mark as "Solved" → Success story
END
```

---

## Missing Flow Components to Implement

### Priority 1: Critical Flows (Enable Core Value)
1. **Dynamic Profile Data Loading** (4A)
   - GET /api/v1/users/me integration
   - Display real activity feed

2. **Settings Backend Integration** (4C)
   - Profile updates
   - Notification preferences
   - Password changes

3. **Analytics Dashboard Data Binding** (5A)
   - Connect charts to real API data
   - Interactive visualizations

4. **Watchlist Functionality** (4A)
   - Add/remove opportunities to watchlist
   - Backend endpoint + frontend UI

### Priority 2: Enhanced User Experience
5. **Email Verification** (1A, 1C)
   - POST /api/v1/auth/verify-email
   - Email sending service integration

6. **Password Reset Backend** (1C)
   - POST /api/v1/auth/request-reset
   - POST /api/v1/auth/reset-password

7. **Impact Points System** (4A, 8A)
   - Calculate points for actions
   - Display leaderboard

8. **Badges System** (4A, 8A)
   - Define badge criteria
   - Award badges automatically

### Priority 3: Advanced Features
9. **Notifications** (4C)
   - Email notifications
   - In-app notifications
   - Push notifications

10. **OAuth Login** (1B)
    - Google OAuth integration
    - GitHub OAuth integration

11. **Admin Flows**
    - User management dashboard
    - Content moderation
    - Analytics for admins

12. **Payment/Subscription** (Future)
    - Stripe integration
    - Subscription tiers
    - Usage limits

---

## API Endpoint Coverage Map

| User Flow | Required Endpoints | Status |
|-----------|-------------------|--------|
| Registration | POST /api/v1/auth/register | ✅ |
| Login | POST /api/v1/auth/login | ✅ |
| Browse Opportunities | GET /api/v1/opportunities | ✅ |
| Filter Opportunities | GET /api/v1/opportunities?filters | ✅ |
| Search | POST /api/v1/opportunities/search | ✅ |
| Create Opportunity | POST /api/v1/opportunities | ✅ |
| Duplicate Check | POST /api/v1/analytics/check-duplicate | ✅ |
| Validate | POST /api/v1/validations | ✅ |
| Remove Validation | DELETE /api/v1/validations/{id} | ✅ |
| Comment | POST /api/v1/comments | ✅ |
| Like Comment | PUT /api/v1/comments/{id}/like | ✅ |
| Feasibility Analysis | GET /api/v1/analytics/feasibility/{id} | ✅ |
| Top Feasible | GET /api/v1/analytics/top-feasible | ✅ |
| Geographic Filter | GET /api/v1/analytics/geographic/* | ✅ |
| Completion Stats | GET /api/v1/analytics/completion-stats | ✅ |
| Get Profile | GET /api/v1/users/me | ✅ |
| Update Profile | PUT /api/v1/users/me | ✅ |
| Password Reset Request | POST /api/v1/auth/request-reset | (depends on deployment) |
| Password Reset | POST /api/v1/auth/reset-password | (depends on deployment) |
| Email Verification | POST /api/v1/auth/verify-email | (depends on deployment) |
| Watchlist Add | POST /api/v1/users/me/watchlist | (planned) |
| Watchlist Remove | DELETE /api/v1/users/me/watchlist/{id} | (planned) |
| Notifications | GET /api/v1/notifications | (planned) |
| OAuth Login | POST /api/v1/auth/oauth/{provider} | (depends on deployment) |

### Monetization / access control endpoints (time-decay + one-time purchases)
- `POST /api/v1/subscriptions/pay-per-unlock` (Pay-per-unlock + Fast Pass PaymentIntent creation)
- `POST /api/v1/subscriptions/confirm-pay-per-unlock` (confirm unlock + grant access)
- `GET /api/v1/subscriptions/unlocks` (list one-time unlock history + expiries)
- `POST /api/v1/subscriptions/checkout` (subscription checkout)
- `POST /api/v1/subscriptions/portal` (billing portal)
- `POST /api/v1/payments/deep-dive` (create Deep Dive $49 PaymentIntent)
- `POST /api/v1/payments/confirm` (confirm generic payment intents, e.g. Deep Dive)
- `POST /api/v1/webhook/stripe` (Stripe webhooks)

---

## Frontend Component Coverage Map

| User Flow | Required Components | Status |
|-----------|-------------------|--------|
| Registration | signup.html + form handler | ✅ |
| Login | login.html + form handler | ✅ |
| Dashboard | index.html + app.js | ✅ |
| Filters | Filter UI + event handlers | ✅ |
| Search | search.html + search logic | ✅ |
| Opportunity Cards | createOpportunityCard() | ✅ |
| Duplicate Warning | showDuplicateWarning() | ✅ |
| Validation Button | validateExisting() | ✅ |
| Comments | Comment section UI | ✅ |
| Profile Display | profile.html | ⚠️ Static |
| Profile Edit | settings.html profile section | ⚠️ Partial |
| Settings Tabs | settings.html tabs | ⚠️ UI only |
| Analytics Dashboard | Research Dashboard tab | ⚠️ Placeholder |
| Feasibility Charts | Chart components | ❌ |
| Watchlist UI | Watchlist section | ❌ |
| Notifications UI | Notification center | ❌ |
| Badges Display | Badge components | ❌ |

---

## Next Steps for Implementation

### Phase 1: Align monetization + gating UX (Week 1-2)
1. Publish a single “tier × opportunity-age” decision matrix (HOT 0-7, FRESH 8-30, VALIDATED 31-90, ARCHIVE 91+).
2. Wire Opportunity cards + detail views to the API’s gated `content_state` (e.g. `full`, `preview`, `locked`, `pay_per_unlock`, `fast_pass`) and render consistent CTAs.
3. Implement “locked” UX: countdown/unlock date + Upgrade CTA (use server-provided eligibility where possible).
4. Implement pay-per-unlock UX ($15, 30-day expiry, daily limit 5): purchase, success state, “already unlocked until …”, and unlock history in Account.
5. Ensure one-time add-ons show clear rules + expiry in the UI:
   - Deep Dive add-on ($49) eligibility + “already unlocked” behavior
   - Fast Pass ($99) eligibility + “already unlocked” behavior

### Phase 2: Subscription lifecycle hardening (Week 3-4)
6. Ensure upgrade/downgrade/cancel paths work both via in-app controls and Stripe Billing Portal; verify downgrades retain one-time unlocks.
7. Add webhook observability for money-moving actions: idempotency, retry visibility, admin surface area for failures.
8. Add post-payment and lifecycle email touchpoints (receipt, upgrade/downgrade, unlock expiring/expired).

### Phase 3: Growth + measurement (Week 5-8)
9. Instrument key events (`upgrade_modal_viewed`, `checkout_started`, `pay_per_unlock_intent_created`, `fast_pass_purchased`, etc.) and validate funnels.
10. Run A/B tests for upgrade prompts (timing/copy) and pay-per-unlock pricing/limits.
11. Decide + implement trials and refund policy (and associated webhook + entitlement logic).

### Phase 4: Platform expansion (Future)
12. Persona-based onboarding paths (founder / scout / investor / corporate) + tailored dashboards.
13. Marketplace + network expansion (experts, execution partners, templates).
14. Deeper “AI co-founder” workflows (roadmaps, progress tracking, outcomes analytics).

---

**Document Version:** 1.0
**Last Updated:** 2025-12-11
**Status:** Living Document - Update as flows evolve
