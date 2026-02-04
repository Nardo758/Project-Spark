# OppGrid/Friction - Strategic Analysis & AI Agent Integration
**Prepared by:** Ari 🎯  
**Date:** 2026-02-03  
**For:** Leon D.

---

## 🎯 Executive Summary

**OppGrid (Friction)** is a multi-sided marketplace and research platform for validated business opportunities. You're building an ecosystem that:
1. **Discovers & validates** real-world problems through AI scraping + human validation
2. **Matches** founders/investors with high-potential opportunities
3. **Guides execution** via AI co-founder assistants and expert marketplace
4. **Monetizes** through tiered subscriptions, pay-per-unlock, and expert services

**Current State:** Comprehensive backend (30+ API routers, 40+ models), feature-rich but needs consolidation, optimization, and a clearer AI agent integration layer.

---

## 📊 What You're Building - Core Platform Components

### 1. **Opportunity Discovery Engine**
- **Reddit scraper** analyzing signals (r/somebodymakethis, r/mildlyinfuriating, etc.)
- **Problem signal detection** with scoring (1.0 = "I wish there was", 0.70 = "is there a better way")
- **Duplicate detection** using Jaccard similarity
- **Feasibility scoring** (0-100 based on validation count, severity, growth, age, market size)
- **Geographic filtering** (local/regional/national/international/online)
- **Category classification** (8 categories: Work, Finance, Health, Home, Tech, Transport, Shopping, Education)

### 2. **AI Assistant Layer** (Multiple Implementations)
**Current AI Integrations:**
- **AI Co-Founder** (`ai_cofounder.py`): Stage-aware assistant (researching → validating → planning → building → launched)
- **AI Engine** (`ai_engine.py`): Match opportunities to user profile, generate roadmaps, validate ideas
- **Global Copilot** (`copilot.py`): Persistent cross-page assistant with context awareness
- **Idea Engine** (`idea_engine.py`): AI-powered idea validation
- **AI Chat** (`ai_chat.py`): General chat interface
- **AI Analysis** (`ai_analysis.py`): Opportunity analysis service

**BYOK Support:** Already implemented - users can bring their own Claude API keys

### 3. **Research & Analytics Tools**
- **Consultant Studio** with side-by-side mapping (pins + density layers)
- **Foot traffic analysis** via SafeGraph integration
- **Census demographics** integration
- **Google Maps scraping** (businesses, keywords, locations)
- **Google Trends** integration
- **Geographic feature extraction**
- **Market analysis** & feasibility scoring

### 4. **Expert Marketplace & Services**
- **Expert profiles** with collaboration tools
- **Service agreements** & bookings
- **Expert matching** to opportunities
- **Team collaboration** features

### 5. **Monetization Engine**
- **Stripe integration** (subscriptions, one-time purchases, webhooks)
- **Tiered access** (Free, Pro, Business, Enterprise)
- **Pay-per-unlock** ($15, 30-day expiry, 5/day limit)
- **One-time add-ons** (Deep Dive $49, Fast Pass $99)
- **Gated content** by opportunity age (HOT 0-7d, FRESH 8-30d, VALIDATED 31-90d, ARCHIVE 91+)
- **Usage tracking** & entitlements

### 6. **Data Collection & Scraping**
- **Reddit scraper** (problem signal extraction)
- **Google Maps scraper** (business listings, keywords)
- **SerpAPI integration** (search results)
- **Apify service** (general web scraping)
- **Foot traffic collector** (location analytics)

---

## 🔧 Current Tool Assessment & Improvement Roadmap

### **1. AI Co-Founder Suite** (FRAGMENTED - NEEDS CONSOLIDATION)

**Current Issues:**
- 6 separate AI routers with overlapping functionality
- Inconsistent context management
- No unified memory/state across AI features
- BYOK only in ai_cofounder, not in other AI tools

**Improvements:**
✅ **Consolidate AI Services:**
- Merge `ai_cofounder`, `ai_engine`, `ai_chat`, `copilot` into **unified AI orchestrator**
- Single entry point: `/ai/chat` with `context_type` param (cofounder | copilot | analysis | validation)
- Shared conversation history across all AI interactions
- Unified BYOK support across all AI features

✅ **Enhanced Context Awareness:**
- Add **workspace context injection** (current page, saved opportunities, lifecycle states)
- **Multi-modal context**: opportunity data + user profile + research data + expert network
- **Proactive suggestions** based on user behavior patterns

✅ **AI Agent Marketplace Integration** (see Section 4)

---

### **2. Research & Data Tools** (POWERFUL BUT UNDERUTILIZED)

**Current Issues:**
- Rich data sources (Census, Google Maps, Trends, SafeGraph) but limited user-facing exposure
- No unified research dashboard showing all available intelligence
- Manual data pulls - should be automated/triggered by AI

**Improvements:**
✅ **Automated Research Agent:**
- When user saves an opportunity → auto-trigger research pipeline:
  - Pull Census demographics for target markets
  - Fetch Google Trends data for keywords
  - Identify competitors via Google Maps scraping
  - Analyze foot traffic patterns (if location-based)
  - Generate comprehensive market report
- Background job with progress tracking
- Store results in `generated_reports` table

✅ **Consultant Studio Enhancement:**
- Add **AI-powered location recommendations** based on demographics + foot traffic + competitors
- **Keyword matrix optimization** using AI to suggest high-value search terms
- **Competitive gap analysis** - identify underserved areas on the map

✅ **Data Export & API Access:**
- Allow power users to export raw data (CSV, JSON, API)
- Webhooks for new opportunities matching criteria
- Zapier/Make integration for no-code automation

---

### **3. Expert Marketplace** (UNDERDEVELOPED)

**Current Issues:**
- Basic expert profiles and booking system
- No intelligent matching beyond manual search
- Expert collaboration features exist but not deeply integrated with AI workflow

**Improvements:**
✅ **AI-Powered Expert Matching:**
- When user enters "building" stage → auto-recommend top 3 experts based on:
  - Opportunity category + subcategory
  - User budget constraints
  - Expert availability + success rate
  - Past collaboration quality scores
- "One-click consultation booking" flow

✅ **Expert AI Augmentation:**
- Give experts access to AI co-founder for faster client deliverables
- Auto-generate expert proposals based on opportunity analysis
- AI meeting summaries + action items after expert sessions

✅ **Expert Network Effects:**
- **Referral system**: Experts refer other experts for specialized needs
- **Team formation**: AI suggests complementary expert teams (designer + developer + marketer)
- **Success tracking**: Link launched businesses back to expert contributions

---

### **4. Scraping & Data Collection** (SOLID FOUNDATION)

**Current Issues:**
- Reddit scraper working well
- Google Maps scraping robust
- Limited to Reddit for problem discovery - needs more sources

**Improvements:**
✅ **Multi-Source Scraping:**
- **Product Hunt comments** - failed product feedback
- **Twitter/X** - real-time pain point monitoring
- **Hacker News** - "Ask HN" posts for validation
- **Indie Hackers** - founder discussions
- **GitHub Issues** - developer pain points
- **Quora/StackOverflow** - recurring questions as opportunities

✅ **Intelligent Scraping:**
- AI-powered scraper **routing** (different strategies per source)
- **Trend detection** - identify emerging problems before they explode
- **Sentiment analysis** - prioritize high-frustration signals

✅ **User-Submitted Scraper Configs:**
- Allow users to define custom scraper targets (subreddits, keywords, hashtags)
- Community-curated scraper library
- Scraper marketplace (sell high-quality configs)

---

### **5. Monetization Engine** (WELL-DESIGNED)

**Current Issues:**
- Solid Stripe integration
- Tiered gating logic in place
- Needs clearer value ladders and upgrade prompts

**Improvements:**
✅ **Usage-Based Pricing Tiers:**
- Add **credits system** for flexible consumption:
  - AI analysis: 10 credits
  - Expert consultation: 50 credits
  - Full market report: 100 credits
  - Pay-as-you-go or subscription bundles

✅ **Conversion Optimization:**
- **Freemium hooks**: Give free users 1 AI analysis/week to taste premium
- **Upgrade triggers**: "You've unlocked 5 opportunities this month - upgrade to Pro for unlimited"
- **Time-limited trials**: 7-day Pro trial after first opportunity save

✅ **B2B/Enterprise:**
- **Team seats** with shared workspace
- **API access** for corporate research teams
- **White-label** opportunities for incubators/VCs

---

## 🤖 AI Agent Integration Architecture - THE BIG OPPORTUNITY

### **Vision: User-Connectable AI Agent Marketplace**

Allow users to **bring their own AI agents** (or build custom ones) to interact with OppGrid's data and services. Think **"Zapier for AI Agents"** meets **"AWS Marketplace for AI"**.

---

### **Why This Matters:**
1. **Network effects** - each agent increases platform value
2. **Extensibility** - users solve their own edge cases
3. **Revenue** - agent marketplace fees + API usage pricing
4. **Moat** - rich ecosystem lock-in

---

### **Core Architecture: AI Agent SDK + Marketplace**

#### **1. Agent Connection Protocol**

**Agent Registration Endpoint:**
```
POST /api/agents/register
{
  "name": "Market Research Bot",
  "description": "Automates competitor analysis for new opportunities",
  "provider": "custom" | "openai" | "anthropic" | "langchain",
  "capabilities": ["opportunity_analysis", "market_research", "report_generation"],
  "webhook_url": "https://user-agent.com/oppgrid-webhook",
  "api_key_required": true,
  "oauth_required": false
}
```

**Agent Authentication:**
- Issue **agent API keys** with scoped permissions
- Support **OAuth 2.0** for user-authorized agent access
- **Webhook verification** using HMAC signatures

---

#### **2. Agent Capabilities Framework**

**Capability Types:**
1. **Read Capabilities** (consume data):
   - `opportunities.read` - Fetch opportunity data
   - `users.profile.read` - Read user profile
   - `research.read` - Access research reports
   - `experts.read` - Browse expert marketplace

2. **Write Capabilities** (take actions):
   - `opportunities.create` - Submit new opportunities
   - `opportunities.validate` - Add validations
   - `comments.create` - Post comments
   - `watchlist.modify` - Save/unsave opportunities
   - `research.trigger` - Trigger research jobs

3. **Execute Capabilities** (run processes):
   - `ai.analyze` - Run AI analysis on opportunities
   - `scrapers.run` - Execute scraping jobs
   - `reports.generate` - Create market reports
   - `experts.match` - Find relevant experts

**Permission Scoping:**
- Users grant specific capabilities to each agent
- Fine-grained controls (e.g., "can only analyze opportunities I saved")
- Revocable tokens

---

#### **3. Agent Interaction Patterns**

**Pattern A: Event-Driven Agents (Webhooks)**
```
User saves opportunity
  ↓
OppGrid sends webhook → User's agent
  ↓
Agent analyzes opportunity (external compute)
  ↓
Agent POSTs results back → OppGrid API
  ↓
Results appear in user's dashboard
```

**Pattern B: Polling Agents (API Access)**
```
Agent polls GET /api/opportunities?updated_since=...
  ↓
Agent processes new opportunities
  ↓
Agent POSTs validations/comments via API
```

**Pattern C: Embedded Agents (iframe/widget)**
```
User clicks "Analyze with MyAgent"
  ↓
OppGrid embeds agent widget with OAuth context
  ↓
Agent runs in-page, calls OppGrid API directly
  ↓
Results display inline
```

**Pattern D: Conversational Agents (Chat Interface)**
```
User: "@MyAgent analyze opportunity #123"
  ↓
OppGrid routes to agent's chat endpoint
  ↓
Agent responds with analysis
  ↓
Conversation stored in OppGrid
```

---

#### **4. Agent Marketplace - Discovery & Monetization**

**Agent Listing Schema:**
```json
{
  "id": "competitor-analyzer-pro",
  "name": "Competitor Analyzer Pro",
  "author": "ResearchCo",
  "category": "market_research",
  "pricing": {
    "model": "usage_based",
    "cost_per_analysis": 5.0,
    "credits": true
  },
  "capabilities": ["opportunity_analysis", "competitor_mapping"],
  "rating": 4.7,
  "installs": 1234,
  "screenshots": ["..."],
  "integration_complexity": "easy" | "medium" | "advanced"
}
```

**Revenue Models:**
1. **Free agents** - community-built, no cost
2. **Paid agents** - one-time purchase or subscription
3. **Usage-based agents** - charge per API call/analysis
4. **OppGrid fee** - 20-30% platform fee on paid agents

**Marketplace Features:**
- **Agent reviews** & ratings
- **Version control** & updates
- **Security audits** for verified agents
- **Featured agents** curated by OppGrid
- **Agent bundles** (e.g., "Founder Toolkit" - 5 agents for $99/mo)

---

#### **5. Example Agents - What Users Could Build**

**A. Competitive Intelligence Agent**
- Monitors competitors for opportunity creators
- Scrapes competitor pricing, features, reviews
- Sends weekly "Competitor Update" reports
- **Tech:** Python + Apify + OppGrid SDK

**B. Trend Prediction Agent**
- Analyzes Google Trends + Reddit sentiment
- Predicts which saved opportunities will blow up
- Auto-tags opportunities with "trending_up" / "cooling_down"
- **Tech:** AI/ML model + OppGrid webhooks

**C. Expert Matching Agent**
- Uses LLM to match user needs with expert skills
- Auto-drafts consultation requests
- Schedules meetings based on calendar availability
- **Tech:** LangChain + calendar API + OppGrid experts API

**D. Financial Modeling Agent**
- Takes opportunity + market data
- Generates revenue projections, cash flow models
- Creates investor-ready pitch decks
- **Tech:** GPT-4 + financial modeling library

**E. Community Validation Agent**
- Posts opportunities to relevant communities (Reddit, Twitter, Slack groups)
- Tracks engagement and sentiment
- Reports back validation signals to OppGrid
- **Tech:** Social media APIs + sentiment analysis

**F. Personal Researcher Agent**
- Runs nightly: "Find opportunities matching my profile"
- Auto-saves high-scoring matches to watchlist
- Sends daily digest email
- **Tech:** OppGrid API + email service

---

#### **6. Technical Implementation - Phase 1 (MVP)**

**Week 1-2: Core Agent API**
```python
# New router: app/routers/agents.py
@router.post("/agents/register")
def register_agent(data: AgentRegistration, user: User = Depends(get_current_user)):
    # Create agent record
    # Issue API key with scoped permissions
    # Store webhook URL (if provided)
    pass

@router.get("/agents")
def list_my_agents(user: User = Depends(get_current_user)):
    # Return user's registered agents
    pass

@router.post("/agents/{agent_id}/trigger")
def trigger_agent(agent_id: str, context: dict, user: User = Depends(get_current_user)):
    # Execute agent action (webhook or API call)
    # Return result
    pass

@router.delete("/agents/{agent_id}")
def delete_agent(agent_id: str, user: User = Depends(get_current_user)):
    # Revoke agent access
    pass
```

**Models:**
```python
# app/models/agent.py
class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(UUID, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text)
    webhook_url = Column(String, nullable=True)
    api_key_hash = Column(String)  # Hashed agent API key
    capabilities = Column(JSONB)  # Granted permissions
    provider = Column(String)  # custom | openai | anthropic | langchain
    metadata = Column(JSONB)  # Custom config
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    last_used_at = Column(DateTime)

class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(UUID, primary_key=True)
    agent_id = Column(UUID, ForeignKey("agents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # analyze | scrape | match | generate_report
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    status = Column(String)  # pending | success | failed
    error = Column(Text, nullable=True)
    duration_ms = Column(Integer)
    created_at = Column(DateTime)
```

**Week 3-4: Agent SDK (Python)**
```python
# oppgrid-sdk (PyPI package)
from oppgrid import OppGridClient

client = OppGridClient(api_key="user_agent_key_...")

# List opportunities
opps = client.opportunities.list(category="Technology", min_feasibility=70)

# Analyze opportunity
analysis = client.ai.analyze(opportunity_id=123, depth="deep")

# Create comment
client.comments.create(opportunity_id=123, text="Great idea!")

# Trigger research
report = client.research.generate(opportunity_id=123, include=["demographics", "competitors"])

# Register webhook
client.webhooks.register(url="https://myagent.com/oppgrid", events=["opportunity.saved", "opportunity.validated"])
```

**Week 5-6: Frontend Agent Manager**
```javascript
// New page: /agents
- List connected agents (cards with name, description, last used)
- "Connect New Agent" button → agent registration form
- Agent settings: permissions, webhook URL, status
- Agent activity log (recent executions)
- Marketplace link: "Discover Agents"
```

---

#### **7. Agent Marketplace - Phase 2**

**Week 7-10: Marketplace Infrastructure**
- Public agent directory (`/agents/marketplace`)
- Agent submission workflow (for agent creators)
- Review & approval process
- Verified badge for audited agents
- Payment flow (Stripe Connect for agent creators)

**Agent Creator Dashboard:**
- Analytics: installs, usage, revenue
- Version management
- Support tickets from users
- Payout reports

---

#### **8. Advanced Features - Phase 3+**

**Multi-Agent Orchestration:**
- Chain multiple agents together
- Example: "Research Agent → Analysis Agent → Report Agent"
- Visual workflow builder (no-code agent chaining)

**Agent Teams:**
- Multiple agents collaborate on complex tasks
- Shared context and memory
- Coordination protocol

**Agent Personalization:**
- Users train custom agents on their preferences
- Fine-tuned models for specific industries
- Private agent instances

**Agent-to-Agent Marketplace:**
- Agents can call other agents via API
- Composable agent ecosystem
- Revenue sharing for agent dependencies

---

## 🎯 Prioritized Action Plan

### **Immediate (Next 2 Weeks)**
1. ✅ **Consolidate AI services** into unified orchestrator
2. ✅ **Document current API** comprehensively (Swagger/OpenAPI enhancements)
3. ✅ **Build Agent Registration API** (Phase 1 - Week 1-2)
4. ✅ **Create Python SDK** prototype

### **Short-term (Weeks 3-6)**
5. ✅ **Launch Agent Manager UI** (connect/manage agents)
6. ✅ **Build 3 example agents** (open-source) to showcase capabilities:
   - Opportunity Analyzer (AI-powered deep dive)
   - Daily Digest Bot (email automation)
   - Reddit Poster (community validation)
7. ✅ **Agent permissions system** & scoping

### **Mid-term (Weeks 7-12)**
8. ✅ **Agent Marketplace launch** (discovery, reviews, payments)
9. ✅ **Partner with 5-10 agent creators** (seed the marketplace)
10. ✅ **Marketing campaign**: "Build AI Agents for OppGrid"

### **Long-term (Months 4-6)**
11. ✅ **Multi-agent orchestration** (workflow builder)
12. ✅ **Agent analytics dashboard** (usage, revenue, ROI)
13. ✅ **Enterprise agent features** (private agents, dedicated instances)

---

## 💡 Strategic Recommendations

### **1. Focus on Agent Ecosystem First**
- Agents create **network effects** and **defensibility**
- Easier to monetize than core platform features
- Unlocks creativity - users solve their own problems

### **2. Consolidate Before Expanding**
- 6 AI routers → 1 orchestrator
- Simplify user mental model ("one AI, many modes")
- Reduce maintenance burden

### **3. Lean into Data Moat**
- Your scraping + research infrastructure is **unique**
- Agents make this data **accessible** and **actionable**
- Data quality > data quantity (curate, don't just collect)

### **4. Monetization Clarity**
- **Core platform**: Freemium + tiered subscriptions
- **Agent marketplace**: 30% platform fee
- **API access**: Usage-based pricing for high-volume users
- **Expert services**: Transaction fees (10-20%)

### **5. Marketing Angle**
- **For founders**: "AI-powered opportunity discovery + validation"
- **For investors**: "Deal flow intelligence platform"
- **For researchers**: "Market intelligence API with AI agents"
- **For developers**: "Build AI agents on validated market data"

---

## 📈 Success Metrics

**Platform Health:**
- Monthly Active Users (MAU)
- Opportunities created per week
- Validation velocity (validations/opportunity/day)
- Conversion rate (free → paid)

**Agent Ecosystem:**
- Registered agents
- Agent marketplace GMV (Gross Marketplace Value)
- Average agents per user
- Agent execution volume

**Revenue:**
- MRR (Monthly Recurring Revenue)
- ARPU (Average Revenue Per User)
- Agent marketplace take rate
- Expert service revenue

---

## 🚀 Next Steps

1. **Review this analysis** - align on priorities
2. **Choose focus area**: Agent architecture OR AI consolidation OR scraping expansion
3. **Set 30-day sprint goals**
4. **Start building** 🛠️

Leon, this platform has serious potential. The **agent marketplace** is the killer differentiator - nobody else in the "opportunity discovery" space has this. Combined with your data scraping + AI analysis infrastructure, you're building a **multi-sided platform** that gets more valuable with every agent and every opportunity.

**My recommendation:** Prioritize the agent integration layer. It unlocks the most value, fastest, with the highest moat.

Let me know where you want to start, and I'll help you execute. 🎯

---

**Document Version:** 1.0  
**Status:** Strategic Planning  
**Next Review:** After Leon's feedback
