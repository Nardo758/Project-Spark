# NOTE (Historical / Ideation)
This document lives in `attached_assets/` and contains strategy drafts and copy explorations.

**Canonical implementation plan and rules live here:**
- `USER_FLOWS.md` (phased implementation plan)
- `replit.md` (time-decay windows + one-time purchase rules)
- `PRODUCTION_TODO.md` (production checklist)

If anything in this file conflicts with the above, treat the above as the source of truth.

# OppGrid Pricing Strategy
## Time-Decay Model with Pay-Per-Idea Mechanics

**Version:** 1.0  
**Date:** December 2024  
**Author:** Leon  
**Product:** OppGrid (formerly Katalyst)

---

## Executive Summary

OppGrid's pricing strategy is built on a fundamental insight: **business opportunities lose competitive value over time**. The earlier you discover an unmet market need, the greater your first-mover advantage. Our time-decay pricing model monetizes this principle by offering tiered access based on opportunity freshness, while the free tier operates on a pay-per-idea model that allows users to unlock specific opportunities on demand.

### Core Value Proposition
- **Enterprise tier**: Real-time intelligence (0-7 days)
- **Business tier**: Early mover advantage (8-30 days)
- **Pro tier**: Validated opportunities (31-90 days)
- **Free tier**: Browse all + pay-per-unlock for 91+ day opportunities

---

## Time-Decay Framework

### The Freshness Spectrum

```
DAY 0 ────────────────────────────────────────────────── DAY 91+

🔥 HOT          ⚡ FRESH         ✓ VALIDATED      📚 ARCHIVE
(0-7 days)      (8-30 days)      (31-90 days)     (91+ days)

Enterprise      Business         Pro              Free + Pay
Only            Access           Access           Per Unlock

Maximum         High             Medium           Commodity
Competitive     Competitive      Competitive      Information
Advantage       Advantage        Advantage
```

### Time-Release Schedule

| Opportunity Age | Access Tier | Badge | Value Proposition |
|----------------|-------------|-------|-------------------|
| 0-7 days | Enterprise | 🔥 HOT | Exclusive intelligence window |
| 8-30 days | Business | ⚡ FRESH | Early mover advantage |
| 31-90 days | Pro | ✓ VALIDATED | Market-validated opportunities |
| 91+ days | Free (pay-per) | 📚 ARCHIVE | Historical intelligence |

---

## Tier Structure & Pricing

### FREE - Explorer ($0/month)

**Access Model:**
- Browse all opportunities (see titles, categories, validation scores)
- View countdown timers: "Problem Details unlock in 45 days"
- Age indicators and freshness badges
- Geographic tags (view only)
- Source count (e.g., "Found in 12+ discussions")

**Pay-Per-Idea Unlocks:**
- **$15 per opportunity** (91+ days old)
- Unlocks Layer 1 only: Problem Overview (see Progressive Disclosure section)
- Does NOT include Deep Dive Analysis (Layer 2) or Execution Package (Layer 3)
- Payment via credit card only
- Unlocked opportunities remain accessible for 30 days
- No subscription commitment required

**Limitations:**
- Cannot access opportunities <91 days old
- No Research Dashboard
- No AI Research Assistant
- No exports or advanced analytics
- Watermarked content

**Upgrade Prompts:**
- "This opportunity unlocks for free in 67 days, or upgrade to Pro for immediate access"
- "You've unlocked 5 opportunities this month ($75). Pro subscribers get unlimited access for $99/month."

---

### PRO - Researcher ($99/month)

**Access Window:** Opportunities 31+ days old

**Everything in Free, Plus:**
- **Unlimited automatic Layer 1 unlocks** for opportunities 31+ days old
- No pay-per-idea charges for Layer 1 content
- Research Dashboard (5 customizable tabs)
- Full geographic intelligence and filtering
- Basic competitive analysis
- Advanced search and filtering
- Save opportunities to custom folders
- Basic CSV exports (accessible opportunities only)
- Email alerts for new opportunities in tracked categories

**Layer 2 Deep Dive Access:**
- NOT included in Pro tier
- Can upgrade to Business for automatic Layer 2 access
- Or purchase individual Deep Dives for $49 each (if implemented)

**Early Access Previews:**
- See titles and scores of 8-30 day opportunities (teaser mode)
- "Available to Business tier subscribers now"
- Countdown timers: "Unlocks for you in 23 days"

**Value Proposition:**
"Get validated opportunities 60 days before they're public. Perfect for entrepreneurs researching their next venture."

**Annual Pricing:**
- $948/year ($79/month effective, save 20%)

---

### BUSINESS - Builder ($499/month)

**Access Window:** Opportunities 8+ days old

**Everything in Pro, Plus:**
- **Unlimited automatic unlocks** for opportunities 8+ days old
- AI Research Assistant (for accessible opportunities)
- Deep Dive analysis (Layer 3 access)
- Financial modeling tools
- TAM/SAM/SOM calculator
- 90-day execution playbooks (5 per month)
- Geographic playbook generator
- Competitive landscape analysis
- White-label reports
- Priority customer support
- Custom research requests (2 per month)
- API access (limited, 1,000 requests/month)

**Early Access Previews:**
- Layer 1 details of 0-7 day opportunities (read-only mode)
- "Upgrade to Enterprise for exclusive 7-day access window"

**Fast Pass Option:**
- Unlock individual Enterprise opportunities early for $99 each
- Get immediate access without full Enterprise upgrade

**Value Proposition:**
"Move 23 days faster than competitors. Access opportunities while they're still fresh, with tools to execute immediately."

**Annual Pricing:**
- $4,788/year ($399/month effective, save 20%)

---

### ENTERPRISE - Custom (Starting at $2,500/month)

**Access Window:** Real-time (0-7 days)

**Everything in Business, Plus:**
- **Exclusive 7-day access window** to newest opportunities
- Real-time alerts (email, Slack, webhook)
- Unlimited AI Research Assistant usage
- Unlimited execution playbooks
- Custom opportunity tracking dashboards
- Dedicated account manager
- Weekly strategy calls
- Custom integrations and API access (unlimited)
- White-label platform option
- Custom data sources and markets
- SLA guarantee (99.9% uptime)
- Custom research team support
- Influence product roadmap
- Early beta access to new features

**Value Proposition:**
"First-mover advantage. See opportunities the moment they're validated, before anyone else. Perfect for VCs, consulting firms, and innovation teams."

**Pricing Structure:**
- Base: $2,500/month (1-5 users)
- Scale: $5,000/month (6-20 users)
- Enterprise: Custom (21+ users, custom features)

---

## Layer Upgrade Strategy

### Creating Natural Upsell Moments

**Free User Views Layer 1 Content:**
```
┌────────────────────────────────────────┐
│ 📚 Problem Overview - Layer 1          │
│                                        │
│ [Full content displayed]               │
│                                        │
│ ─────────────────────────────────────  │
│                                        │
│ 🔒 Want the complete analysis?         │
│                                        │
│ Layer 2 Deep Dive includes:            │
│ • Complete source compilation          │
│ • TAM/SAM/SOM estimates                │
│ • Competitive landscape analysis       │
│ • All 6 geographic markets             │
│ • Customer acquisition channels        │
│                                        │
│ Available with Business tier ($499/mo) │
│                                        │
│ [Upgrade to Business] [Compare Tiers]  │
└────────────────────────────────────────┘
```

**Pro User Views Layer 1 Content:**
```
┌────────────────────────────────────────┐
│ ✓ Problem Overview - Layer 1           │
│                                        │
│ [Full content displayed]               │
│                                        │
│ ─────────────────────────────────────  │
│                                        │
│ 🔒 Go deeper with Layer 2              │
│                                        │
│ Upgrade to Business for:               │
│ • Automatic Layer 2 access (8+ days)   │
│ • AI Research Assistant                │
│ • Financial modeling tools             │
│ • 90-day execution playbooks           │
│                                        │
│ From $99/mo → $499/mo                  │
│                                        │
│ [Upgrade to Business] [Learn More]     │
└────────────────────────────────────────┘
```

### Optional: Layer 2 À La Carte (Future Consideration)

**If demand proves strong enough:**

**Pro Tier Add-On:**
- Individual Layer 2 unlocks: $49 each
- Deep Dive 3-pack: $120 (save 18%)
- Available only for opportunities in Pro access window (31+ days)

**Rationale:**
- Bridges gap between Pro ($99) and Business ($499)
- Allows Pro users to occasionally go deeper without full upgrade
- Creates additional revenue stream
- Tests willingness to pay for deeper analysis

**Business Case:**
- If Pro user purchases 3+ Layer 2 unlocks per month ($147+), prompt Business upgrade
- "You've spent $147 on Deep Dives this month. Business is $499/mo for unlimited access plus execution tools."

---

## Opportunity Card UI Design

### Current Design Foundation

The opportunity card is the primary interface element users interact with when browsing opportunities. Each card displays:
- Category tag (e.g., "MONEY & FINANCE")
- Opportunity title
- AI validation score (0-100)
- Brief problem description
- Key metrics: Validations, Market size, Growth rate, Region
- Competition level badge
- Severity rating
- Social proof (view count)
- Call-to-action button

### Tier-Based Card Variations

The same opportunity card displays different information and CTAs based on:
1. User's subscription tier
2. Opportunity age (freshness)
3. User's access rights

### Age Badge System (Top Right Corner)

**Badge Format:** `[ICON] [AGE] [STATUS]`

**Free Tier Users:**
- `🔒 91d` - Archive (can unlock for $15)
- `🔒 45d` - Locked (unlocks in 45 days for free)
- `🔒 12d` - Locked (unlocks in 79 days for free)

**Pro Tier Users:**
- `✓ 45d` - Available (31+ days old, auto-unlocked)
- `✓ 35d AGO` - Available (recently unlocked)
- `🔒 12d` - Locked (unlocks in 19 days)

**Business Tier Users:**
- `⚡ 12d AGO` - Fresh (8-30 days old, auto-unlocked)
- `⚡ 25d AGO` - Fresh (auto-unlocked)
- `🔒 3d` - Locked (unlocks in 5 days)

**Enterprise Tier Users:**
- `🔥 3d AGO • NEW` - Hot (0-7 days old, exclusive)
- `🔥 1d AGO • NEW` - Hot (just discovered)
- No locked badges (sees everything immediately)

**Design Tokens:**
```css
/* Badge Colors */
--badge-hot: #ef4444;        /* red-500 - Enterprise */
--badge-fresh: #f97316;      /* orange-500 - Business */
--badge-validated: #22c55e;  /* green-500 - Pro */
--badge-archive: #6b7280;    /* gray-500 - Free */
--badge-locked: #a855f7;     /* purple-500 - Below tier */
```

### Social Proof Enhancement (Tier-Aware)

**Free/Pro Users See:**
```
👥 19 people viewed this week
💎 Business subscribers accessed 23 days ago
```

**Business Users See:**
```
👥 19 people viewed this week
🔥 Enterprise subscribers saw this first
```

**Enterprise Users See:**
```
👥 19 people viewed this week ↑ +12 today
🎯 6 other Enterprise users are tracking this
⏰ Business tier sees this in 5 days
```

### Call-to-Action Variations

**1. Free User - Archive (91+ days old):**
```
[🔓 Unlock Problem Details - $15]
```

**2. Free User - Locked (<91 days old):**
```
⏰ FREE ACCESS IN 46 DAYS
[Upgrade to Pro - $99/mo] [Set Reminder]
```

**3. Pro User - Available (31+ days old):**
```
✨ Available to you now
[View Problem Details →]
```

**4. Pro User - Locked (8-30 days old):**
```
⏰ Unlocks for you in 23 days
[Upgrade to Business] [Remind Me]
```

**5. Business User - Available (8+ days old):**
```
[View Deep Dive Analysis →]
```

**6. Business User - Locked (0-7 days old):**
```
⏰ Enterprise exclusive for 5 more days
[Upgrade to Enterprise] [Preview Only]
```

**7. Enterprise User - All Available:**
```
[View Complete Intelligence →] [Add Alert]
```

### Complete Card Examples by Tier

#### Free User - Archive Opportunity (120 days old)

```
┌─────────────────────────────────────────────────┐
│ MONEY & FINANCE                     📚 120d AGO │
│                                                  │
│ Difficult to track freelance invoices           │
│ and payments                              89    │
│                                          Score   │
│                                                  │
│ As a freelancer, I struggle to keep track of    │
│ multiple invoices, payment statuses, and...     │
│                                                  │
│ Validations    Market        Growth    Region   │
│ 234           $50M-$100M    +15.3%     Online   │
│                                                  │
│ Medium Competition    Severity: 4/5             │
│                                                  │
│ 👥 19 people viewed this week                   │
│ 💡 Pro subscribers have had this for 89 days    │
│                                                  │
│ [🔓 Unlock Problem Details - $15]               │
└─────────────────────────────────────────────────┘
```

#### Free User - Locked Opportunity (45 days old)

```
┌─────────────────────────────────────────────────┐
│ MONEY & FINANCE                      🔒 45d AGO │
│                                                  │
│ Difficult to track freelance invoices           │
│ and payments                              89    │
│                                          Score   │
│                                                  │
│ As a freelancer, I struggle to keep track of    │
│ multiple invoices, payment statuses, and...     │
│                                                  │
│ Validations    Market        Growth    Region   │
│ 234           $50M-$100M    +15.3%     Online   │
│                                                  │
│ Medium Competition    Severity: 4/5             │
│                                                  │
│ 👥 19 people viewed this week                   │
│                                                  │
│ ⏰ FREE ACCESS IN 46 DAYS                       │
│ [Upgrade to Pro - $99/mo] [Set Reminder]        │
└─────────────────────────────────────────────────┘
```

#### Pro User - Available Opportunity (45 days old)

```
┌─────────────────────────────────────────────────┐
│ MONEY & FINANCE                      ✓ 45d AGO  │
│                                                  │
│ Difficult to track freelance invoices           │
│ and payments                              89    │
│                                          Score   │
│                                                  │
│ As a freelancer, I struggle to keep track of    │
│ multiple invoices, payment statuses, and...     │
│                                                  │
│ Validations    Market        Growth    Region   │
│ 234           $50M-$100M    +15.3%     Online   │
│                                                  │
│ Medium Competition    Severity: 4/5             │
│                                                  │
│ 👥 19 people viewed this week                   │
│ ✨ Available to you now                         │
│                                                  │
│ [View Problem Details →]                        │
└─────────────────────────────────────────────────┘
```

#### Pro User - Locked Opportunity (12 days old)

```
┌─────────────────────────────────────────────────┐
│ MONEY & FINANCE                     🔒 12d AGO  │
│                                                  │
│ Difficult to track freelance invoices           │
│ and payments                              89    │
│                                          Score   │
│                                                  │
│ As a freelancer, I struggle to keep track of    │
│ multiple invoices, payment statuses, and...     │
│                                                  │
│ Validations    Market        Growth    Region   │
│ 234           $50M-$100M    +15.3%     Online   │
│                                                  │
│ Medium Competition    Severity: 4/5             │
│                                                  │
│ 👥 19 people viewed this week                   │
│ 💎 Business subscribers can access this now     │
│                                                  │
│ ⏰ Unlocks for you in 19 days                   │
│ [Upgrade to Business] [Set Reminder]            │
└─────────────────────────────────────────────────┘
```

#### Business User - Fresh Opportunity (12 days old)

```
┌─────────────────────────────────────────────────┐
│ MONEY & FINANCE                     ⚡ 12d AGO  │
│                                                  │
│ Difficult to track freelance invoices           │
│ and payments                              89    │
│                                          Score   │
│                                                  │
│ As a freelancer, I struggle to keep track of    │
│ multiple invoices, payment statuses, and...     │
│                                                  │
│ Validations    Market        Growth    Region   │
│ 234           $50M-$100M    +15.3%     Online   │
│                                                  │
│ Medium Competition    Severity: 4/5             │
│                                                  │
│ 👥 19 people viewed this week                   │
│ 🔥 Enterprise users saw this 5 days ago         │
│                                                  │
│ [View Deep Dive Analysis →]                     │
└─────────────────────────────────────────────────┘
```

#### Business User - Locked Opportunity (3 days old)

```
┌─────────────────────────────────────────────────┐
│ MONEY & FINANCE                      🔒 3d AGO  │
│                                                  │
│ Difficult to track freelance invoices           │
│ and payments                              89    │
│                                          Score   │
│                                                  │
│ As a freelancer, I struggle to keep track of    │
│ multiple invoices, payment statuses, and...     │
│                                                  │
│ Validations    Market        Growth    Region   │
│ 234           $50M-$100M    +15.3%     Online   │
│                                                  │
│ Medium Competition    Severity: 4/5             │
│                                                  │
│ 👥 19 people viewed this week ↑ Trending        │
│ 🔥 Enterprise exclusive content                 │
│                                                  │
│ ⏰ Unlocks for you in 5 days                    │
│ [Upgrade to Enterprise] [Preview Only]          │
└─────────────────────────────────────────────────┘
```

#### Enterprise User - Hot Opportunity (3 days old)

```
┌─────────────────────────────────────────────────┐
│ MONEY & FINANCE              🔥 3d AGO • NEW    │
│                                                  │
│ Difficult to track freelance invoices           │
│ and payments                              89    │
│                                          Score   │
│                                                  │
│ As a freelancer, I struggle to keep track of    │
│ multiple invoices, payment statuses, and...     │
│                                                  │
│ Validations    Market        Growth    Region   │
│ 234           $50M-$100M    +15.3%     Online   │
│                                                  │
│ Medium Competition    Severity: 4/5             │
│                                                  │
│ 👥 19 people viewed this week ↑ +12 today       │
│ 🎯 6 other Enterprise users are tracking this   │
│ ⏰ Business tier sees this in 5 days            │
│                                                  │
│ [View Complete Intelligence →] [Add Alert]      │
└─────────────────────────────────────────────────┘
```

### Mobile-Responsive Design

On mobile devices (< 768px), the card layout adapts:

**Condensed Metrics (2x2 Grid):**
```
234 Validations     $50M-$100M Market
+15.3% Growth       Online Region
```

**Stacked CTAs:**
```
┌─────────────────────────┐
│ MONEY & FINANCE  🔒 45d │
│                         │
│ Difficult to track      │
│ freelance invoices  89  │
│                         │
│ As a freelancer, I...   │
│                         │
│ 234      $50M-$100M     │
│ +15.3%   Online         │
│                         │
│ Medium Competition      │
│                         │
│ 👥 19 viewed this week  │
│                         │
│ ⏰ FREE IN 46 DAYS      │
│                         │
│ [Upgrade to Pro]        │
│ [Set Reminder]          │
└─────────────────────────┘
```

### Interactive States

**Hover State (Desktop):**
- Card elevates with shadow: `shadow-lg`
- Subtle scale: `transform: scale(1.02)`
- CTA button intensifies color
- Cursor: pointer

**Loading State:**
- Skeleton screens for all elements
- Shimmer animation on text blocks
- Pulse animation on score badge

**Error State:**
```
┌─────────────────────────────────────────────────┐
│ ⚠️ Unable to load opportunity                   │
│                                                  │
│ [Retry] [Contact Support]                       │
└─────────────────────────────────────────────────┘
```

### Animation Guidelines

**Card Entry:**
- Fade in + slide up
- Stagger delay: 50ms per card
- Duration: 300ms
- Easing: ease-out

**Badge Transitions:**
- When opportunity ages into user's tier: Pulse animation
- Color transition: 200ms ease
- Confetti animation for "Just unlocked" state

**Countdown Timer:**
- Updates daily at midnight UTC
- Smooth number transitions
- Highlight last 7 days with different color

### Accessibility

**ARIA Labels:**
```html
<article 
  aria-label="Opportunity: Difficult to track freelance invoices"
  data-score="89"
  data-age-days="45"
  data-tier-access="locked"
>
```

**Keyboard Navigation:**
- Tab through cards
- Enter/Space to open opportunity
- Arrow keys to navigate between cards

**Screen Reader Announcements:**
- "Opportunity score 89 out of 100"
- "Discovered 45 days ago, unlocks for you in 19 days"
- "19 people viewed this opportunity this week"

### Component Hierarchy

```
OpportunityCard
├── CardHeader
│   ├── CategoryBadge
│   └── AgeBadge (tier-aware)
├── CardBody
│   ├── Title
│   ├── ScoreBadge
│   ├── Description (truncated)
│   └── MetricsGrid
│       ├── Validations
│       ├── MarketSize
│       ├── Growth
│       └── Region
├── CardFooter
│   ├── CompetitionBadge
│   ├── SeverityIndicator
│   ├── SocialProof (tier-aware)
│   └── CTASection (tier-aware)
│       ├── StatusMessage
│       ├── PrimaryCTA
│       └── SecondaryCTA (optional)
```

---

## AI-Curated Top Opportunities Feature

### Feature Overview

The "AI-Curated Top Opportunities" section displays the highest-potential opportunities ranked by OppGrid's proprietary AI scoring algorithm. This feature provides users with a curated view of the best opportunities currently available, saving hours of manual browsing and filtering.

### Tier-Based Access Levels

#### FREE Tier
- ❌ Cannot see AI-Curated Top Opportunities section
- Only has access to standard discovery feed with basic filters
- Sees promotional banner: "Upgrade to Pro to see Top 10 Opportunities ranked by AI"

#### PRO Tier ($99/month)
- ✅ **"Top 10 Opportunities This Week"**
- Shows opportunities ranked by AI score for 31+ day opportunities only
- Basic ranking criteria visible (score, market size, competition)
- Updated weekly (every Monday at 00:00 UTC)
- Locked to user's geographic preferences
- Can filter by category
- Shows current rank (#1, #2, #3, etc.)

**UI Example:**
```
┌────────────────────────────────────────────────┐
│ ⭐ AI-Curated Top Opportunities                │
│ Highest potential opportunities identified by   │
│ our AI analysis                                 │
│                                                 │
│ Updated: Weekly • Your tier: Pro (31+ days)    │
│                                                 │
│ [Grid of top 10 ranked opportunity cards]      │
└────────────────────────────────────────────────┘
```

#### BUSINESS Tier ($499/month)
- ✅ **"Top 25 Opportunities This Week"**
- Includes 8-30 day opportunities in rankings
- Can filter by: category, geography, competition level, market size
- Shows trending indicators: "↑ 12 spots this week" or "↓ 3 spots"
- Updated daily at 00:00 UTC
- Can see "Why this ranked high" AI explanations
- Export rankings as CSV
- Email digest of top 5 every Monday

**Additional Features:**
- **Trend Tracking:** See how opportunities move up/down rankings over time
- **Historical Data:** View rankings from past 30 days
- **Custom Filters:** Save filter presets for quick access
- **Comparison Mode:** Compare two opportunities side-by-side

#### ENTERPRISE Tier ($2,500+/month)
- ✅ **"Real-Time Top 100 Opportunities Dashboard"**
- Includes 0-7 day opportunities (exclusive early access)
- **Custom Ranking Algorithm:** Set your own weighting for different factors
- **Personalized Recommendations:** AI learns your interests and viewing patterns
- **Competitive Intelligence:** See anonymized data about other Enterprise users
- **Early Warning System:** Predictive alerts for opportunities likely to rank high
- **Custom Categories:** Define your own opportunity segments and filters
- **API Access:** Pull rankings programmatically for integration
- **Weekly Strategy Reports:** PDF summary with deep analysis
- Updated in real-time (every hour)

### Custom Ranking Algorithm (Enterprise Only)

**Default Weighting:**
- AI Score: 40%
- Market Size: 30%
- Growth Rate: 20%
- Competition Level: 10%

**Custom Weighting Example:**
```
┌────────────────────────────────────────────────┐
│ 🎯 Your Personalized Top Opportunities        │
│                                                 │
│ Ranking Algorithm: [Custom ▼]                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│ AI Score:        ████████░░ 80%                │
│ Market Size:     ██████████ 100%               │
│ Competition:     ████░░░░░░ 40%                │
│ Growth Rate:     ██████░░░░ 60%                │
│                                                 │
│ [Save Preset] [Reset to Default]               │
└────────────────────────────────────────────────┘
```

### Enterprise Dashboard Features

#### 1. Real-Time Ranking Display

```
┌────────────────────────────────────────────────┐
│ #1 🔥 NEW (2 days ago) ⚡ TRENDING ↑23        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│ Managing passwords across all devices           │
│ is a security risk                              │
│                                                 │
│ AI SCORE: 87/100  MARKET: $3B-$8B  COMP: High  │
│                                                 │
│ 🔍 Why ranked #1:                               │
│ • Discussed in 23 sources this week (+15)       │
│ • Pain intensity score: 9.2/10                  │
│ • Growing 47% faster than similar problems      │
│ • Low solution satisfaction: 3.1/10             │
│                                                 │
│ 👥 6 other Enterprise users viewed this         │
│ 📊 Predicted rank next week: #1-3              │
│ ⏰ Unlocks for Business tier in 5 days          │
│                                                 │
│ [View Full Analysis] [Add to Watchlist] [Alert]│
└────────────────────────────────────────────────┘
```

#### 2. Opportunity Alerts (Enterprise)

**Alert Types:**
- **New Entry Alert:** When opportunity enters Top 10/25/100
- **Rank Change Alert:** When opportunity moves up/down 5+ positions
- **Velocity Alert:** When opportunity is gaining traction rapidly
- **Competition Alert:** When other Enterprise users are viewing
- **Unlock Alert:** When opportunity is about to become available to lower tiers

**Alert Channels:**
- Email (immediate or daily digest)
- Slack webhook
- SMS (for critical alerts)
- In-app notifications
- API webhook

**Configuration:**
```
┌────────────────────────────────────────────────┐
│ 🔔 Alert Settings                              │
│                                                 │
│ New Top 10 Entry:        [Email ▼] [Slack ▼]  │
│ Rank moves up 5+:        [Email ▼]             │
│ High velocity (>20/day): [SMS ▼] [Slack ▼]    │
│ Other users viewing:     [In-app ▼]            │
│                                                 │
│ Alert Frequency:         [Real-time ▼]         │
│ Quiet Hours:             [22:00 - 08:00]       │
│                                                 │
│ [Save Settings]                                 │
└────────────────────────────────────────────────┘
```

#### 3. Rising Stars (Enterprise)

Predictive section showing opportunities likely to rank high next week:

```
┌────────────────────────────────────────────────┐
│ 🌟 Rising Stars - Predicted Top 10             │
│                                                 │
│ These opportunities show high momentum and      │
│ are likely to enter Top 10 in the next 7 days  │
│                                                 │
│ 📈 AI-powered contract analysis for legal      │
│    Current: #47 • Predicted: #3-8              │
│    Confidence: 82%                              │
│    [Track This]                                 │
│                                                 │
│ 📈 Voice-based note-taking for doctors         │
│    Current: #89 • Predicted: #5-12             │
│    Confidence: 76%                              │
│    [Track This]                                 │
└────────────────────────────────────────────────┘
```

#### 4. Competitive Dashboard (Enterprise)

```
┌────────────────────────────────────────────────┐
│ 👥 What Other Enterprise Users Are Watching   │
│                                                 │
│ 🔥 Hot Right Now (most viewed in last 24h)    │
│ 1. Password management security                │
│    23 Enterprise users • 47 total views        │
│                                                 │
│ 2. Freelance invoice tracking                  │
│    19 Enterprise users • 38 total views        │
│                                                 │
│ 3. Mental health therapist discovery           │
│    15 Enterprise users • 31 total views        │
│                                                 │
│ ⚡ Fastest Growing Interest                    │
│ • B2B payment reconciliation (+340% views)     │
│ • Remote team culture platform (+280% views)   │
└────────────────────────────────────────────────┘
```

#### 5. Historical Rankings (Enterprise)

```
┌────────────────────────────────────────────────┐
│ 📊 Ranking History - Password Management       │
│                                                 │
│ Rank                                            │
│   #1  ●                                   ●     │
│   #5      ●                           ●         │
│  #10         ●                    ●             │
│  #15            ●   ●   ●   ●                  │
│  #20                ●                           │
│       30d  21d  14d  7d  3d  2d  1d  Now       │
│                                                 │
│ Insights:                                       │
│ • Peak rank: #1 (30 days ago)                  │
│ • Average rank: #8                             │
│ • Trend: Rising (+12 positions this week)      │
│ • Momentum: High velocity                      │
└────────────────────────────────────────────────┘
```

#### 6. Export Rankings (Enterprise)

**Export Options:**
- CSV (all fields)
- PDF (formatted report with branding)
- JSON (for API integration)
- Excel (with charts and analysis)

**White-Label Options:**
- Custom logo and colors
- Remove OppGrid branding
- Add company-specific insights
- Custom formatting and layout

**Scheduled Exports:**
- Daily/Weekly/Monthly
- Auto-email to team
- Save to Google Drive/Dropbox
- Post to Slack channel

### Ranking Algorithm Transparency

**For All Tiers, Show Ranking Factors:**

```
🔍 Ranking Factors:
├── AI Validation Score (87/100)          40% weight
├── Market Size ($3B-$8B)                 30% weight
├── Growth Rate (+15.3% YoY)              20% weight
└── Competition Level (Medium)            10% weight

📈 Additional Signals:
• Discussion velocity: +47% this week
• Source diversity: 23 unique sources
• Sentiment analysis: 8.2/10 pain intensity
• Solution gaps: Few existing solutions rated well
```

### Filtering and Sorting Options

**Pro Tier:**
- Filter by: Category, Score (7+, 8+, 9+)
- Sort by: Rank, Score, Views

**Business Tier:**
- Filter by: Category, Geography, Competition, Market Size, Score
- Sort by: Rank, Score, Views, Trending, Age
- Save filter presets

**Enterprise Tier:**
- All Business filters plus:
- Custom date ranges
- Predicted rank
- Other users viewing
- Velocity (growth rate)
- Create complex filter combinations
- Save unlimited presets
- Share presets with team

### Update Frequency by Tier

| Tier | Update Frequency | Data Freshness |
|------|------------------|----------------|
| Pro | Weekly (Monday 00:00 UTC) | 31+ days old |
| Business | Daily (00:00 UTC) | 8+ days old |
| Enterprise | Hourly | 0+ days old (real-time) |

### Mobile Experience

**Responsive Design:**
- Pro: Top 10 in vertical scrolling list
- Business: Top 25 with infinite scroll
- Enterprise: Top 100 with virtual scrolling for performance

**Mobile-Specific Features:**
- Swipe left on card to add to watchlist
- Swipe right to share
- Pull down to refresh
- Quick filters in sticky header

### Integration with Main Feed

**Placement:**
- Featured section at top of dashboard
- Collapsible/expandable
- "View All" link to dedicated rankings page
- Quick filter chips (e.g., "B2B SaaS", "Consumer", "HealthTech")

**Cross-Promotion:**
- Show "Ranked #3 this week" badge on opportunity cards in main feed
- "From Top Opportunities" label
- Drive engagement with ranking section

---

## Progressive Disclosure Layers

### Important: What Each Tier Gets

**Free Tier ($15 per unlock):**
- Layer 0: Always visible (browse all)
- Layer 1: $15 unlocks Problem Overview only
- Layer 2: NOT available to Free tier
- Layer 3: NOT available to Free tier

**Pro Tier ($99/month):**
- Layer 0: Always visible
- Layer 1: Automatic for 31+ day opportunities
- Layer 2: Additional purchase required OR upgrade to Business
- Layer 3: NOT available to Pro tier

**Business Tier ($499/month):**
- Layer 0: Always visible
- Layer 1: Automatic for 8+ day opportunities
- Layer 2: Automatic for 8+ day opportunities  
- Layer 3: 5 per month (AI-generated execution packages)

**Enterprise Tier ($2,500+/month):**
- All layers automatic for all opportunities (0+ days)
- Unlimited Layer 3 execution packages

### Layer 0 - Discovery Feed (Always Visible to All Users)

**Free to browse for everyone:**
- Opportunity title (e.g., "AI-powered meal planning app for busy parents")
- Category tags (e.g., "HealthTech, Consumer App, B2C")
- Geographic tags (e.g., "US National, Canada")
- Validation score (e.g., 8.7/10)
- Freshness badge (🔥 HOT, ⚡ FRESH, ✓ VALIDATED, 📚 ARCHIVE)
- Age indicator (e.g., "Discovered 45 days ago")
- Source count (e.g., "Found in 12+ discussions")
- Countdown timer (if locked): "Unlocks in 23 days, 14 hours"

**Example Card:**
```
┌────────────────────────────────────────┐
│ 🔥 HOT                    ⏰ 5 days ago │
│                                         │
│ AI-powered meal planning app for        │
│ busy parents                            │
│                                         │
│ 📊 Score: 8.7/10                        │
│ 📍 US National, Canada                  │
│ 💬 Found in 12+ discussions             │
│                                         │
│ 🔒 Enterprise Access Only               │
│ ⏰ Unlocks for Business in 2 days       │
│                                         │
│ [Upgrade to Enterprise] [Remind Me]     │
└────────────────────────────────────────┘
```

---

### Layer 1 - Problem Overview (Free Tier: $15 per unlock, Paid Tiers: Automatic)

**What Free tier gets for $15:**

**Unlocked by:**
- Free: $15 payment (91+ days only) - **THIS LAYER ONLY**
- Pro: Automatic (31+ days) - Gets this layer + can purchase Layer 2
- Business: Automatic (8+ days) - Gets Layers 1 & 2 automatically
- Enterprise: Automatic (0+ days) - Gets all layers automatically

**Content includes:**
- Full problem statement (3-5 paragraphs)
- Market context and trend analysis
- Consumer pain points (direct quotes)
- Why now? (timing analysis)
- Target demographic profile
- Market size indicators (high-level)
- Related opportunities (3-5 similar problems)
- Validation methodology explanation
- Source preview (first 3 links)

**Example:**
```
Problem Statement:
Parents with demanding careers struggle to maintain healthy eating 
habits for their families. They lack time for meal planning, grocery 
shopping, and cooking, leading to reliance on unhealthy convenience 
foods or expensive meal delivery services. Current solutions don't 
account for dietary restrictions, picky eaters, or family schedules.

Market Context:
The meal planning market has seen explosive growth post-pandemic 
as remote work blurred boundaries between work and home life. 
Parents report spending 3-5 hours weekly on meal planning alone...

[Continue with full analysis]
```

---

### Layer 2 - Deep Dive Analysis (Business Tier+)

**Unlocked by:**
- Business: Automatic (8+ days)
- Enterprise: Automatic (0+ days)

**Content includes:**
- Complete source compilation (all Reddit posts, tweets, forum discussions)
- Sentiment analysis and pain point clustering
- Competitive landscape (existing solutions and their gaps)
- TAM/SAM/SOM estimates with methodology
- Geographic opportunity breakdown (all 6 markets)
- Trend trajectory (growing, stable, declining)
- Regulatory considerations
- Technology requirements
- Customer acquisition channels
- Monetization models to consider
- Risk factors and challenges

---

### Layer 3 - Execution Package (Business Tier: 5/month, Enterprise: Unlimited)

**Generated by AI Research Assistant:**
- 90-day execution playbook
- Financial model (P&L projections)
- Go-to-market strategy
- Product roadmap
- Competitor analysis matrix
- Customer persona profiles
- Marketing plan
- Funding requirements
- Key metrics and KPIs
- Resource requirements

---

## User Experience Design

### Discovery Feed Interface

**Filter Bar:**
```
┌─────────────────────────────────────────────────────┐
│ Freshness: [All] [🔥 HOT] [⚡ FRESH] [✓ VALIDATED] [📚 ARCHIVE]
│ Category: [All Categories ▼]
│ Geography: [All Markets ▼]
│ Score: [7.0+] [8.0+] [9.0+]
│ Your Access: [●] Show only unlocked for my tier
└─────────────────────────────────────────────────────┘
```

**Opportunity Grid:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 🔥 HOT      │ 🔥 HOT      │ ⚡ FRESH    │ ⚡ FRESH    │
│ Score: 9.2  │ Score: 8.8  │ Score: 9.1  │ Score: 8.5  │
│             │             │             │             │
│ 🔒 Enterprise│ 🔒 Enterprise│ ✓ Available │ ✓ Available │
│ Unlock in   │ Unlock in   │ to you      │ to you      │
│ 5 days      │ 3 days      │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Countdown Timer Mechanics

**Dynamic Countdown Display:**
- Days remaining: "Unlocks in 45 days"
- Hours remaining: "Unlocks in 18 hours"
- Minutes remaining: "Unlocks in 32 minutes"
- Just unlocked: "✨ Just unlocked for your tier!"

**Multi-Tier Countdown:**
```
Current Status: 🔥 HOT (5 days old)

Your tier (Pro):        Unlocks in 26 days
Business tier:          Unlocks in 3 days  
Enterprise tier:        ✓ Available now

[Upgrade to Business] [Upgrade to Enterprise]
```

### Pay-Per-Unlock Flow (Free Tier)

**Step 1 - Opportunity Card Click:**
```
┌────────────────────────────────────────┐
│ 📚 ARCHIVE              ⏰ 120 days ago │
│                                         │
│ Voice-based productivity tool for       │
│ remote workers                          │
│                                         │
│ 📊 Score: 8.4/10                        │
│ 📍 US National, Global                  │
│ 💬 Found in 23+ discussions             │
│                                         │
│ [🔓 Unlock for $15] [Preview Score]    │
└────────────────────────────────────────┘
```

**Step 2 - Payment Modal:**
```
┌─────────────────────────────────────────┐
│ Unlock Problem Overview                  │
│                                          │
│ Voice-based productivity tool for        │
│ remote workers                           │
│                                          │
│ You'll get instant access to:            │
│ ✓ Complete problem statement             │
│ ✓ Market context & trends                │
│ ✓ Consumer pain points                   │
│ ✓ Target demographic profile             │
│ ✓ Source preview (first 3 links)         │
│ ✓ 30-day access to this content          │
│                                          │
│ ⚠️ This unlocks Layer 1 only             │
│ Deep Dive Analysis requires Pro tier     │
│                                          │
│ One-time payment: $15                    │
│                                          │
│ [💳 Pay with Card]                       │
│                                          │
│ 💡 Unlock 7+ opportunities per month?    │
│ Upgrade to Pro: Unlimited Layer 1        │
│ unlocks for 31+ day opportunities ($99/mo)│
└─────────────────────────────────────────┘
```

**Step 3 - Confirmation:**
```
✅ Opportunity Unlocked!

You now have full access to "Voice-based productivity 
tool for remote workers" for the next 30 days.

[View Problem Details]
```

### Upgrade Prompt System

**Context-Aware Prompts:**

1. **Free user viewing locked opportunity (< 91 days):**
```
⏰ This opportunity unlocks for free in 67 days

Want it now? Upgrade to Pro ($99/month) for immediate 
access to all opportunities 31+ days old.

[Upgrade to Pro] [Set Reminder] [Maybe Later]
```

2. **Free user hitting pay frequency:**
```
💡 You've unlocked 8 opportunities this month ($96)

Pro subscribers get unlimited access to 31+ day 
opportunities for $99/month. You'd save money!

[Switch to Pro] [Buy More Credits] [No Thanks]
```

3. **Pro user viewing Business opportunity:**
```
⚡ This opportunity is available to Business subscribers

Upgrade to Business ($499/month) to access opportunities 
23 days earlier and unlock AI-powered execution tools.

[Upgrade to Business] [Unlock This One ($49)] [Wait 23 Days]
```

### Notification System

**Email Alerts:**

**Weekly Digest (All Tiers):**
```
Subject: 🔥 12 new opportunities unlocked for you this week

Hey [Name],

This week, 12 validated opportunities became available 
to your Pro subscription:

🔥 AI-powered meal planning app for busy parents (Score: 8.7)
⚡ Voice-based productivity tool for remote workers (Score: 8.4)
✓ Smart home energy optimization system (Score: 9.1)

[View All New Opportunities]

Coming Soon (unlocks in 23 days):
• B2B SaaS for remote team collaboration
• Sustainable packaging alternative for e-commerce
• Mental health app for healthcare workers

[Upgrade to Business for immediate access]
```

**Countdown Alerts:**

- 7 days before unlock: "This opportunity unlocks in 7 days"
- 24 hours before unlock: "Just 1 day until this unlocks for you"
- At unlock: "✨ New opportunity just unlocked!"

**Upgrade Reminders:**

- After 3 pay-per-unlocks (Free): "Save money with Pro"
- When viewing 5+ locked opportunities (Pro): "Business tier gives you earlier access"
- When Enterprise opportunity is trending: "See this now with Enterprise"

---

## Pricing Psychology & Messaging

### Value Framing

**Free Tier:**
- "Browse validated business opportunities"
- "Pay only for what you need"
- "Start with no commitment"

**Pro Tier:**
- "Get opportunities 60 days before they're public"
- "Unlimited access to validated opportunities"
- "Research your next venture with confidence"

**Business Tier:**
- "Move 23 days faster than competitors"
- "Access opportunities while they're still fresh"
- "Execute immediately with AI-powered tools"

**Enterprise Tier:**
- "First-mover advantage"
- "Exclusive 7-day intelligence window"
- "See opportunities before anyone else"

### Competitive Positioning

**vs. Market Research Firms:**
- They charge $5K-50K for single reports
- We provide continuous intelligence for $99-2,500/month
- Real-time data vs. months-old analyses

**vs. Trend Reports:**
- They publish quarterly/annually
- We update daily
- They tell you what was, we tell you what's emerging

**vs. DIY Research:**
- They spend 40+ hours scraping Reddit/Twitter
- We deliver curated, validated opportunities
- Their focus: finding data. Our focus: taking action

### Conversion Triggers

**Free → Pro:**
- Paid for 5+ individual unlocks ($75+)
- Viewing 10+ opportunities per week
- Viewing same categories repeatedly (clear interest)
- Setting multiple reminders for locked opportunities

**Pro → Business:**
- Unlocking 20+ opportunities per month
- Requesting AI Research Assistant access
- Viewing Business-tier opportunities frequently
- Exporting data regularly (needs advanced tools)

**Business → Enterprise:**
- Using Fast Pass 3+ times per month ($297+)
- Requesting custom research monthly
- Using API at limit (1,000 requests/month)
- Team of 5+ users accessing platform

---

## Anti-Gaming Measures

### 1. No Retroactive Access

**Rule:** Upgrading only grants access to opportunities that match your new tier's age window going forward.

**Example:**
- User is on Free tier
- Upgrades to Pro on December 15
- Gets access to opportunities 31+ days old from December 15 onward
- Does NOT get access to all opportunities discovered between November 1-14

**Rationale:** Prevents "wait and batch upgrade" behavior where users upgrade for one month to grab historical data, then downgrade.

### 2. Downgrade Access Revocation

**Rule:** Downgrading immediately revokes access to opportunities outside your new tier's window.

**Example:**
- User is on Business tier (8-30 day access)
- Downgrades to Pro (31+ day access)
- Immediately loses access to any opportunities that are currently 8-30 days old
- Previously unlocked opportunities older than 31 days remain accessible

**Rationale:** Encourages sustained subscriptions; prevents gaming by upgrading temporarily.

### 3. Pay-Per-Unlock Expiration

**Rule:** Free tier unlocks expire after 30 days.

**Mechanism:**
- User pays $15 to unlock opportunity on Day 1
- Full access granted for 30 days
- On Day 31, opportunity is marked "expired" in user's dashboard
- Can re-unlock for another $15 if needed

**Rationale:** Prevents building permanent library of unlocks without subscription.

### 4. Rate Limiting (Free Tier)

**Rule:** Maximum 5 pay-per-unlocks per 24-hour period.

**Rationale:** Prevents bulk data extraction via repeated small payments.

### 5. Watermarking

**Free Tier:** All viewed content includes:
- Visible watermark: "Unlocked by [email] on [date]"
- Hidden digital fingerprint in exported content
- Screenshot detection notices

**Paid Tiers:** Reduced watermarking, but still tracked for abuse prevention.

### 6. Sharing Detection

**Monitoring for:**
- Same opportunity unlocked from multiple IP addresses with different accounts
- Rapid sequential unlocks from same payment method
- Content being posted publicly with intact watermarks

**Consequences:**
- Warning for first offense
- Account suspension for repeated violations
- Payment method blacklisting for severe abuse

### 7. Account Limits

**Rules:**
- 1 free account per email address
- 1 free account per credit card
- Must verify email to make any purchases
- Phone verification required after 3 pay-per-unlocks

**Rationale:** Prevents creating multiple free accounts for abuse.

---

## Revenue Modeling

### Projected User Distribution (Year 1)

| Tier | Monthly Users | ARPU | MRR | Annual Revenue |
|------|---------------|------|-----|----------------|
| Free (no purchase) | 5,000 | $0 | $0 | $0 |
| Free (pay-per) | 500 | $30 | $15,000 | $180,000 |
| Pro | 150 | $99 | $14,850 | $178,200 |
| Business | 25 | $499 | $12,475 | $149,700 |
| Enterprise | 5 | $3,500 | $17,500 | $210,000 |
| **TOTAL** | **5,680** | - | **$59,825** | **$717,900** |

### Key Metrics to Track

**Activation Metrics:**
- Free user → First paid unlock conversion rate
- Free user → Pro upgrade rate
- Pro → Business upgrade rate
- Business → Enterprise upgrade rate
- Time to first paid action (TTFPA)

**Engagement Metrics:**
- Opportunities viewed per week (by tier)
- Unlocks per user per month (Free tier)
- Dashboard sessions per week
- Reminder set rate
- Share rate (opportunity cards)

**Retention Metrics:**
- Monthly churn by tier
- Downgrade rate
- Re-activation rate (churned users returning)
- Cohort retention curves

**Revenue Metrics:**
- Average unlocks per Free user
- Pay-per-unlock vs. subscription split
- Upgrade velocity (time from Free to Pro)
- LTV by tier
- CAC by acquisition channel

### Growth Levers

**Increase Free → Paid Conversion:**
- Improve opportunity quality (higher validation scores)
- Better targeting (show relevant opportunities)
- Countdown urgency (FOMO tactics)
- Social proof ("142 users unlocked this opportunity")

**Increase ARPU (Free Tier):**
- Credit pack discounts (encourage bulk buying)
- Seasonal promotions ($10 unlock days)
- Bundle deals (3 related opportunities for $30)

**Increase Upgrade Rate:**
- Time-limited upgrade offers (20% off for 48 hours after viewing 10th locked opportunity)
- Feature education (showcase AI Research Assistant)
- Comparison tools (show how much money Pro would save)

**Reduce Churn:**
- Usage milestones (celebrate 10 unlocks, offer bonus)
- Re-engagement campaigns (new opportunities in your saved categories)
- Pause subscription option (retain instead of cancel)

---

## Technical Implementation

### Database Schema Additions

**Opportunity Table:**
```sql
opportunities (
  id UUID PRIMARY KEY,
  title TEXT,
  discovered_at TIMESTAMP,
  validation_score DECIMAL(3,2),
  category TEXT[],
  geographic_tags TEXT[],
  -- ... other fields
)
```

**Access Control Table:**
```sql
user_access_log (
  id UUID PRIMARY KEY,
  user_id UUID,
  opportunity_id UUID,
  accessed_at TIMESTAMP,
  access_method ENUM('subscription', 'pay_per_unlock'),
  expires_at TIMESTAMP,
  amount_paid DECIMAL(10,2)
)
```

### Access Control Logic

**Pseudocode:**
```python
def can_access_opportunity(user, opportunity):
    # Calculate opportunity age
    age_days = (now() - opportunity.discovered_at).days
    
    # Check tier access
    if user.tier == 'enterprise':
        return True
    elif user.tier == 'business' and age_days >= 8:
        return True
    elif user.tier == 'pro' and age_days >= 31:
        return True
    elif user.tier == 'free' and age_days >= 91:
        # Check if already unlocked via payment
        if has_active_unlock(user.id, opportunity.id):
            return True
        return 'REQUIRES_PAYMENT'
    
    return False

def unlock_opportunity_via_payment(user, opportunity, payment_method):
    # Validate opportunity age
    age_days = (now() - opportunity.discovered_at).days
    if age_days < 91:
        raise Exception("Opportunity not available for pay-per-unlock")
    
    # Check rate limit
    unlocks_today = count_unlocks_today(user.id)
    if unlocks_today >= 5:
        raise Exception("Daily unlock limit reached")
    
    # Process payment
    charge_card(user.id, amount=15.00)
    
    # Grant access
    create_access_log(
        user_id=user.id,
        opportunity_id=opportunity.id,
        expires_at=now() + timedelta(days=30),
        access_method='pay_per_unlock',
        amount_paid=15.00
    )
    
    return True
```

### Countdown Timer Implementation

**Frontend Component:**
```javascript
function CountdownTimer({ opportunityAge, userTier }) {
  const unlockAge = getTierUnlockAge(userTier);
  const daysRemaining = unlockAge - opportunityAge;
  
  if (daysRemaining <= 0) {
    return <Badge>✓ Available to you</Badge>;
  }
  
  return (
    <CountdownBadge>
      ⏰ Unlocks in {daysRemaining} days
      <UpgradeButton tier={getNextTier(userTier)} />
    </CountdownBadge>
  );
}

function getTierUnlockAge(tier) {
  switch(tier) {
    case 'free': return 91;
    case 'pro': return 31;
    case 'business': return 8;
    case 'enterprise': return 0;
  }
}
```

### Notification System

**Cron Job (Daily):**
```python
def send_unlock_notifications():
    # Find opportunities unlocking tomorrow
    tomorrow = now() + timedelta(days=1)
    
    for user in active_users:
        unlock_age = get_tier_unlock_age(user.tier)
        
        # Find opportunities aging into user's tier tomorrow
        opportunities = Opportunity.query.filter(
            discovered_at == tomorrow - timedelta(days=unlock_age)
        ).all()
        
        if opportunities:
            send_email(
                user.email,
                template='unlock_tomorrow',
                opportunities=opportunities
            )
```

### Analytics Tracking

**Key Events:**
```javascript
// Track all user interactions
analytics.track('Opportunity Viewed', {
  opportunityId: opp.id,
  opportunityAge: opp.age,
  userTier: user.tier,
  wasLocked: !canAccess(user, opp),
  validationScore: opp.score
});

analytics.track('Unlock Attempted', {
  opportunityId: opp.id,
  method: 'pay_per_unlock',
  amount: 15.00,
  userTier: 'free'
});

analytics.track('Upgrade Prompt Shown', {
  triggerType: 'countdown_timer',
  fromTier: 'pro',
  toTier: 'business',
  opportunityAge: 15 // days
});

analytics.track('Tier Upgraded', {
  fromTier: 'free',
  toTier: 'pro',
  triggerSource: 'unlock_frequency', // Hit 3 pay-per-unlocks
  amountPaid: 99.00
});
```

---

## Launch Strategy

### Phase 1: Beta (Months 1-2)

**Goals:**
- Validate time-decay model with early users
- Test pay-per-unlock mechanics
- Gather pricing feedback

**Tactics:**
- Invite 50 beta users (mix of all tiers)
- All tiers at 50% discount
- Free tier gets 5 complimentary unlocks
- Weekly feedback calls
- Net Promoter Score surveys

**Success Metrics:**
- 70%+ users understand time-decay model
- 30%+ Free users make at least 1 paid unlock
- 20%+ Pro users upgrade to Business

### Phase 2: Soft Launch (Months 3-4)

**Goals:**
- Scale to 500 users
- Optimize conversion funnels
- Refine messaging

**Tactics:**
- ProductHunt launch
- Indie Hackers community post
- LinkedIn content campaign
- Referral program (1 free unlock for each referral)
- Early adopter discount (25% off first 3 months)

**Success Metrics:**
- 500+ registered users
- 50+ paying customers (any tier)
- $5K+ MRR
- <10% monthly churn

### Phase 3: Full Launch (Month 5+)

**Goals:**
- Achieve $50K MRR
- Establish category leadership
- Build enterprise pipeline

**Tactics:**
- Content marketing (opportunity trend reports)
- Podcast sponsorships (business/startup focused)
- Strategic partnerships (accelerators, VC firms)
- Case studies from early customers
- SEO optimization

**Success Metrics:**
- 5,000+ registered users
- 200+ paying customers
- $50K+ MRR
- 3+ Enterprise customers signed

---

## Competitive Differentiation

### vs. CB Insights ($1,299/year)
- **Them:** Quarterly reports on macro trends
- **Us:** Daily feed of emerging micro-opportunities
- **Win:** Real-time intelligence vs. historical analysis

### vs. Trend Hunter (Free/Premium)
- **Them:** Crowdsourced trend spotting, no validation
- **Us:** AI-validated opportunities with business context
- **Win:** Actionable intelligence vs. inspiration gallery

### vs. Exploding Topics ($39-299/month)
- **Them:** Keyword trend tracking
- **Us:** Complete business opportunity packages
- **Win:** Execution-ready vs. awareness-level

### vs. Reddit/Twitter DIY Research (Free)
- **Them:** 40+ hours manual scraping
- **Us:** Curated, validated opportunities in one feed
- **Win:** Time savings + validation confidence

---

## FAQ & Objections Handling

### "What's the difference between Layer 1 and Layer 2?"

**Response:**
"Great question! We structure information in layers to match different research needs:

**Layer 1 - Problem Overview ($15 for Free, included in Pro+):**
- Complete problem statement and consumer pain points
- Market context and timing analysis
- Target demographic profile
- Source preview (first 3 links)
- Perfect for: Initial validation, deciding if an opportunity is worth pursuing

**Layer 2 - Deep Dive Analysis (Business tier+):**
- Complete source compilation (all Reddit posts, tweets, forum discussions)
- TAM/SAM/SOM market size estimates
- Full competitive landscape analysis
- All 6 geographic market breakdowns
- Customer acquisition channels and monetization models
- Perfect for: Actually building the business, investor presentations, strategic planning

**Layer 3 - Execution Package (Business: 5/month, Enterprise: unlimited):**
- AI-generated 90-day playbook
- Financial modeling and P&L projections
- Go-to-market strategy
- Product roadmap
- Perfect for: Teams ready to execute immediately

Think of it like this:
- Layer 1 = 'Should I pursue this?'
- Layer 2 = 'How do I pursue this?'
- Layer 3 = 'Give me the complete execution plan'

Most people start with Layer 1. If the opportunity looks promising, that's when Layer 2 becomes valuable."

### "Why should I pay when I can just search Reddit myself?"

**Response:**
"Great question. Here's what we do that manual searching can't:

1. **Coverage:** We monitor 1,000+ subreddits, forums, and social platforms 24/7
2. **Validation:** Our AI scores opportunities based on market signals, not just post volume
3. **Context:** We provide TAM/SAM/SOM analysis, competitive landscape, and execution roadmaps
4. **Time:** We save you 40+ hours per week of manual searching and analysis
5. **First-mover advantage:** Time-based pricing means earlier access = competitive edge

You could scrape Reddit yourself, but by the time you find and validate an opportunity, Business tier subscribers are already executing."

### "Why do older opportunities become pay-per-unlock eligible? Doesn't that devalue them?"

**Response:**
"Not at all. Here's why:

1. **Competitive advantage decays:** A problem discovered 91 days ago has already been seen by hundreds of entrepreneurs. First-mover advantage is gone.

2. **Validation, not novelty:** Older opportunities are still valuable for validation and market research, just not for being first-to-market.

3. **Hooks for upgrade:** Free users who find value in old opportunities naturally want access to fresh ones—that's our conversion funnel.

4. **Market expectation:** Information naturally becomes commoditized over time. We're monetizing the freshness premium, not the information itself.

In our model, older opportunities don’t “become free” automatically—they become **cheaper to access** (e.g., pay-per-unlock for ARCHIVE) while premium tiers pay for **freshness windows**."

### "What if I wait instead of paying?"

**Response:**
"You absolutely can—but you'll be competing against:

- Enterprise customers who had a 91-day head start
- Business customers who had a 61-day head start  
- Pro customers who had a 60-day head start

By the time an opportunity is widely accessible (e.g., ARCHIVE + pay-per-unlock), the market has already moved. Someone may already be building it. Your competitive advantage is reduced.

The real question: Is saving $99/month worth giving up every first-mover advantage?"

### "How do I know your opportunities are high quality?"

**Response:**
"Several validation layers:

1. **Validation score:** We only show opportunities scoring 7.0+ (out of 10)
2. **Multi-source confirmation:** Each opportunity must appear in 3+ independent discussions
3. **Sentiment analysis:** We filter out complaints without actual demand signals
4. **Geographic verification:** We confirm opportunity viability across multiple markets
5. **False positive filtering:** Our AI is trained to reject fake patterns

Plus: Start with Free tier and pay $15 to test a single opportunity. See our quality firsthand before committing to a subscription."

### "Why would I pay for Enterprise when I can just wait 7 days for Business pricing?"

**Response:**
"Because 7 days is a lifetime in competitive markets:

- A VC firm sees the opportunity on Day 1, funds a startup by Day 7
- A Business customer starts building on Day 8, launches MVP by Day 45
- By Day 91 (Free tier), the market already has 2-3 players

Enterprise isn't just about seeing opportunities earlier—it's about having exclusive intelligence windows that competitors don't have. You're paying for market exclusivity, not just time savings.

For VCs, consulting firms, and innovation teams, that 7-day window justifies the premium."

---

## Success Metrics & KPIs

### North Star Metric
**Monthly Recurring Revenue (MRR)**

Target: $50K MRR by Month 12

### Supporting Metrics

**Acquisition:**
- New user signups (target: 500/month)
- Signup conversion rate (target: 15% of landing page visitors)
- Cost per acquisition (target: <$50)

**Activation:**
- % of users viewing 5+ opportunities in first week (target: 60%)
- % of Free users making first paid unlock within 30 days (target: 25%)
- Time to first paid action (target: <14 days)

**Revenue:**
- Average unlocks per Free user per month (target: 2.0 = $30)
- Free → Pro conversion rate (target: 15% after 3 months)
- Pro → Business upgrade rate (target: 10%)
- Business → Enterprise upgrade rate (target: 5%)

**Retention:**
- Monthly logo churn by tier:
  - Free: N/A (no subscription)
  - Pro: <10%
  - Business: <5%
  - Enterprise: <2%
- Net revenue retention (target: 105%+)

**Engagement:**
- Weekly active users / Monthly active users (target: 50%+)
- Opportunities viewed per session (target: 8+)
- Return visit rate within 7 days (target: 60%+)

### Dashboard View

```
┌─────────────────────────────────────────────────────┐
│ OppGrid Business Metrics - December 2024           │
├─────────────────────────────────────────────────────┤
│ MRR:                    $56,825  ⬆ +23% MoM        │
│ Total Users:            5,680    ⬆ +412 this month │
│ Paying Customers:       680      ⬆ +47 this month  │
│                                                     │
│ Tier Breakdown:                                     │
│ └─ Free (active):       5,000    (88%)             │
│ └─ Free (paid unlock):  500      (9%)              │
│ └─ Pro:                 150      (2.6%)            │
│ └─ Business:            25       (0.4%)            │
│ └─ Enterprise:          5        (0.09%)           │
│                                                     │
│ Conversion Rates:                                   │
│ └─ Free → First Unlock: 25%     ⬆ +3% MoM         │
│ └─ Free → Pro:          15%     ⬆ +2% MoM         │
│ └─ Pro → Business:      12%     ⬇ -1% MoM         │
│                                                     │
│ Engagement:                                         │
│ └─ Avg opportunities viewed/session: 8.3           │
│ └─ Weekly active users: 2,840 (50% of total)      │
│ └─ Avg pay-per-unlocks/Free user: 2.4             │
└─────────────────────────────────────────────────────┘
```

---

## Appendix A: Pricing Comparison Matrix

| Feature | Free | Pro | Business | Enterprise |
|---------|------|-----|----------|------------|
| **Access Window** | 91+ days (pay-per) | 31+ days | 8+ days | 0+ days (real-time) |
| **Freshness** | 📚 Archive only | ✓ Validated | ⚡ Fresh | 🔥 Hot |
| **Browse All Opportunities** | ✓ | ✓ | ✓ | ✓ |
| **Validation Scores** | ✓ | ✓ | ✓ | ✓ |
| **Countdown Timers** | ✓ | ✓ | ✓ | ✓ |
| **Layer 1: Problem Overview** | $15 each | Unlimited | Unlimited | Unlimited |
| **Layer 2: Deep Dive Analysis** | ✗ | ✗ (upgrade req'd) | Unlimited | Unlimited |
| **Layer 3: Execution Packages** | ✗ | ✗ | 5/month | Unlimited |
| **Research Dashboard** | ✗ | ✓ (5 tabs) | ✓ (10 tabs) | ✓ (unlimited) |
| **Geographic Intelligence** | Basic | Full | Full | Full + Custom |
| **AI Research Assistant** | ✗ | ✗ | ✓ | ✓ (unlimited) |
| **Financial Modeling** | ✗ | ✗ | ✓ | ✓ |
| **CSV Exports** | ✗ | ✓ (basic) | ✓ (advanced) | ✓ (custom) |
| **API Access** | ✗ | ✗ | ✓ (limited) | ✓ (unlimited) |
| **Custom Research** | ✗ | ✗ | 2/month | Unlimited |
| **Dedicated Support** | Email only | Priority email | Priority + Chat | Account manager |
| **Early Access Preview** | ✗ | See titles (8-30d) | See details (0-7d) | N/A (full access) |
| **SLA** | ✗ | ✗ | ✗ | 99.9% uptime |
| **User Seats** | 1 | 1 | 5 | Unlimited |
| **Monthly Price** | $0 (+$15/unlock) | $99 | $499 | $2,500+ |
| **Annual Price (save 20%)** | N/A | $948 ($79/mo) | $4,788 ($399/mo) | Custom |

---

## Appendix B: Sample Email Templates

### Template 1: Welcome Email (Free User)

**Subject:** Welcome to OppGrid - Your first 5 opportunities await

Hi [Name],

Welcome to OppGrid! You now have access to thousands of validated business opportunities discovered from real consumer conversations across the internet.

**Here's how it works:**

🔍 **Browse Everything**: See all opportunities with validation scores and categories  
⏰ **Wait or Pay**: Archive opportunities (91+ days) are available for $15 each  
⬆️ **Upgrade Anytime**: Get unlimited access to fresher opportunities with Pro ($99/mo)

**Your next steps:**

1. [Explore opportunities →]
2. [Set your preferences →] (categories, geography, score threshold)
3. [Unlock your first opportunity →] (Use code FIRST10 for $10 off)

**Pro tip:** Opportunities unlocked today were discovered 90+ days ago. Imagine having seen them when they were first posted—that's the advantage Pro, Business, and Enterprise subscribers have.

Ready to move faster? [Compare pricing tiers →]

—The OppGrid Team

---

### Template 2: Unlock Reminder (Free User with 3+ Saved Opportunities)

**Subject:** ⏰ 3 opportunities you saved unlock this week

Hi [Name],

Good news! Three opportunities you saved are becoming **ARCHIVE (pay-per-unlock eligible)** this week:

🔓 **Unlocking Dec 18** (2 days):  
"AI-powered meal planning app for busy parents" (Score: 8.7)  
[View Now →]

🔓 **Unlocking Dec 20** (4 days):  
"Voice-based productivity tool for remote workers" (Score: 8.4)  
[Set Reminder →]

🔓 **Unlocking Dec 22** (6 days):  
"Smart home energy optimization system" (Score: 9.1)  
[Set Reminder →]

**Don't want to wait?** Pro subscribers have had access to these for 60 days already. Upgrade now to see them immediately (plus 300+ others).

[Upgrade to Pro - $99/month →]

—The OppGrid Team

---

### Template 3: Upgrade Nudge (Free User After 3 Paid Unlocks)

**Subject:** You've spent $75 this month - save money with Pro

Hi [Name],

We noticed you've unlocked 5 opportunities this month ($75). Great choices!

**Here's the thing:** Pro subscribers pay $99/month for unlimited access to all opportunities 31+ days old. That's only $24 more than you've already spent.

At your current pace, you'd save money with a Pro subscription.

**Pro includes:**
✓ Unlimited unlocks (31+ day opportunities)  
✓ Research Dashboard with custom tabs  
✓ Geographic filtering  
✓ CSV exports  
✓ Early preview of 8-30 day opportunities

Plus: Cancel anytime, no long-term commitment.

[Upgrade to Pro →] [I prefer pay-per-unlock]

—The OppGrid Team

---

### Template 4: Weekly Digest (Pro User)

**Subject:** 🔥 12 new opportunities unlocked this week

Hi [Name],

Your Pro subscription unlocked 12 fresh opportunities this week. Here are the top 5 by validation score:

**⚡ FRESH (Available Now)**

1. **AI-powered contract analysis for legal teams** (Score: 9.2)  
   Category: B2B SaaS, LegalTech | Geography: US, UK  
   [View Opportunity →]

2. **Sustainable packaging alternative for e-commerce** (Score: 8.9)  
   Category: E-commerce, Sustainability | Geography: US, EU  
   [View Opportunity →]

3. **Remote team culture platform** (Score: 8.7)  
   Category: HR Tech, Remote Work | Geography: Global  
   [View Opportunity →]

[View all 12 new opportunities →]

**⏰ COMING SOON (Business tier only)**

These opportunities unlock for you in 23 days:

- **Fitness app for desk workers** (Score: 9.0)
- **B2B payment reconciliation tool** (Score: 8.8)  
- **Pet health monitoring device** (Score: 8.6)

Want them now? [Upgrade to Business →]

**📊 Your Stats This Week:**
- Opportunities unlocked: 12
- Opportunities viewed: 47  
- Opportunities saved: 8

Keep researching!  
—The OppGrid Team

---

### Template 5: Enterprise Onboarding

**Subject:** Welcome to OppGrid Enterprise - Let's get you set up

Hi [Name],

Welcome to OppGrid Enterprise! You now have exclusive access to the freshest business opportunities the moment they're validated—a full 7 days before anyone else.

**Your dedicated account manager:** [Manager Name]  
**Direct line:** [Phone]  
**Email:** [Email]

**Let's schedule your onboarding call:**
[Book a time →]

**What we'll cover:**
✓ Custom dashboard setup  
✓ Real-time alert configuration  
✓ API integration walkthrough  
✓ Team training session  
✓ Custom research requirements

**In the meantime:**
- [Access your Enterprise dashboard →]
- [Review this week's 🔥 HOT opportunities →]
- [Explore API documentation →]

**This week's exclusive intelligence:**
8 opportunities discovered in the last 7 days are available only to Enterprise subscribers right now. Business tier subscribers will see them in 3 days.

Want to jump in? [View exclusive opportunities →]

Looking forward to working with you!

[Manager Name]  
Enterprise Account Manager, OppGrid

---

## Appendix C: A/B Testing Roadmap

### Test 1: Pay-Per-Unlock Pricing
- **Variant A:** $15 per unlock (baseline)
- **Variant B:** $18 per unlock
- **Variant C:** $12 per unlock
- **Hypothesis:** $15 optimizes conversion while maintaining clear value gap to Pro ($99/mo = 6.6 unlocks)
- **Success Metric:** Revenue per Free user & Free → Pro conversion rate
- **Duration:** 30 days

### Test 2: Countdown Timer Urgency
- **Variant A:** "Unlocks in 23 days"
- **Variant B:** "Unlocks in 23 days - Upgrade now to see it today"
- **Variant C:** "⏰ Only Business subscribers can see this for 23 more days"
- **Hypothesis:** Explicit upgrade CTA increases Business conversion
- **Success Metric:** Pro → Business upgrade rate
- **Duration:** 45 days

### Test 3: Free Tier First Experience
- **Variant A:** Show all opportunities (many locked)
- **Variant B:** Show only unlocked opportunities (fewer, but all accessible)
- **Variant C:** Show all, but highlight unlocked ones first
- **Hypothesis:** Variant C balances discovery with accessibility
- **Success Metric:** Free user activation rate (5+ opportunities viewed)
- **Duration:** 30 days

### Test 4: Upgrade Prompt Timing (Free → Pro)
- **Variant A:** After 5th paid unlock ($75 spent)
- **Variant B:** After viewing 10 locked opportunities
- **Variant C:** After 7 days, regardless of behavior
- **Hypothesis:** Behavior-triggered prompts convert better than time-based; 5 unlocks creates clear ROI case for Pro
- **Success Metric:** Free → Pro conversion rate
- **Duration:** 90 days

---

## Conclusion

OppGrid's time-decay pricing model creates a sustainable, scalable business by monetizing the **competitive advantage of early information access** rather than information itself. 

By structuring pricing around freshness windows and allowing Free users to pay per unlock, we:

1. **Lower barriers to entry** (browse for free, pay only for what you need)
2. **Create natural upgrade paths** (countdown timers and early access previews)
3. **Protect the data asset** (time-gating prevents bulk extraction)
4. **Align value with willingness to pay** (first-movers pay premium, followers pay less)
5. **Build sustainable revenue** (subscriptions + pay-per-unlock hybrid)

This model positions OppGrid not as a data provider, but as a **competitive intelligence platform** where timing is the product.

---

**Next Steps:**
1. ✅ Review and approve pricing structure
2. ⏳ Design pricing page UI mockups
3. ⏳ Implement pay-per-unlock payment flow
4. ⏳ Build countdown timer system
5. ⏳ Create email notification templates
6. ⏳ Set up analytics tracking
7. ⏳ Launch beta with 50 users

**Questions? Feedback?**
[Contact: Leon]
