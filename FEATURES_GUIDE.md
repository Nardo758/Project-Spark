# 🚀 Friction API - Features Guide

## Overview

Your Friction API now includes advanced features for geographic filtering, duplicate detection, feasibility analysis, and completion tracking. This guide covers all new capabilities.

---

## 📍 Geographic Features

### Why Geographic Tracking?
Track where problems exist - are they local issues, regional concerns, national problems, or global opportunities?

### Geographic Scopes
- **local** - City or neighborhood level (e.g., "Parking in San Francisco")
- **regional** - State/province level (e.g., "Public transport in California")
- **national** - Country-wide (e.g., "Healthcare costs in USA")
- **international** - Multiple countries (e.g., "International shipping")
- **online** - Internet-based, location-independent (e.g., "Freelance invoicing")

### API Usage

**Filter by Geographic Scope:**
```bash
GET /api/v1/opportunities/?geographic_scope=local
GET /api/v1/opportunities/?geographic_scope=online
```

**Filter by Location:**
```bash
GET /api/v1/opportunities/?country=United%20States
GET /api/v1/opportunities/?country=United%20States&region=California
```

**Geographic Distribution Stats:**
```bash
GET /api/v1/analytics/geographic/distribution
```

Returns:
```json
{
  "scope_distribution": {
    "local": 25,
    "regional": 18,
    "national": 32,
    "international": 15,
    "online": 45
  },
  "top_countries": [
    {"country": "United States", "count": 67},
    {"country": "United Kingdom", "count": 23}
  ]
}
```

---

## 🔍 Duplicate Detection

### Why Duplicate Detection?
Prevent redundant entries and consolidate validation around existing opportunities.

### How It Works
- Uses **Jaccard similarity** to compare text
- Compares both titles and descriptions
- Returns similarity score (0-100%)
- Threshold: 50% similarity = potential duplicate

### API Usage

**Check for Duplicates:**
```bash
POST /api/v1/analytics/check-duplicate
Content-Type: application/json

{
  "title": "Hard to find parking in cities",
  "description": "Takes 30 minutes to find a parking spot downtown"
}
```

Returns:
```json
{
  "is_duplicate": true,
  "duplicate_count": 2,
  "potential_duplicates": [
    {
      "opportunity_id": 5,
      "title": "Finding parking in the city is extremely stressful",
      "similarity_score": 78.5,
      "validation_count": 445,
      "created_at": "2024-12-08T..."
    },
    {
      "opportunity_id": 12,
      "title": "Downtown parking is impossible",
      "similarity_score": 65.2,
      "validation_count": 234,
      "created_at": "2024-11-15T..."
    }
  ]
}
```

### Integration Flow
1. User submits new opportunity
2. Frontend calls `/check-duplicate` first
3. If duplicates found, show them to user
4. User can either:
   - Validate existing opportunity instead
   - Proceed with new submission if truly different

---

## 📊 Feasibility Analysis

### Why Feasibility Scoring?
Help founders and investors identify which opportunities are worth pursuing based on market validation signals.

### Scoring Algorithm (0-100 points)

| Factor | Max Points | Criteria |
|--------|-----------|----------|
| **Validation Count** | 30 | More validations = stronger demand |
| **Severity** | 20 | Higher severity = more important |
| **Growth Rate** | 25 | Positive growth = increasing interest |
| **Age** | 15 | Persistent problems = real need |
| **Market Size** | 10 | Larger market = bigger opportunity |

### Feasibility Levels
- **75-100**: High - Highly feasible, strong validation
- **50-74**: Medium - Moderately feasible, shows promise
- **25-49**: Low - Limited market validation
- **0-24**: Very Low - Insufficient signals

### API Usage

**Get Feasibility Analysis:**
```bash
GET /api/v1/analytics/feasibility/5
```

Returns:
```json
{
  "opportunity_id": 5,
  "feasibility_score": 82.5,
  "feasibility_level": "High",
  "recommendation": "Highly feasible - Strong market validation and growth",
  "metrics": {
    "validation_count": 445,
    "severity": 5,
    "growth_rate": 18.9,
    "market_size": "$100M-$500M",
    "days_active": 45
  }
}
```

**Get Top Feasible Opportunities:**
```bash
GET /api/v1/analytics/top-feasible?limit=10&min_score=60
```

Returns list of highest-scoring opportunities with full details.

**Sort by Feasibility:**
```bash
GET /api/v1/opportunities/?sort_by=feasibility
```

---

## ✅ Completion Tracking

### Why Track Completion?
Monitor which problems get solved, by whom, and how. Learn from successful solutions.

### Completion Statuses
- **open** - Active, unsolved problem
- **in_progress** - Someone is working on it
- **solved** - Problem has been addressed
- **abandoned** - No longer relevant/active

### Tracking Fields
- `completion_status` - Current status
- `solution_description` - How it was solved
- `solved_at` - Timestamp when solved
- `solved_by` - Company/person who solved it

### API Usage

**Update Completion Status:**
```bash
PUT /api/v1/opportunities/5
Content-Type: application/json

{
  "completion_status": "solved",
  "solution_description": "ParkMobile app now provides real-time parking availability in 50+ cities"
}
```

**Filter by Status:**
```bash
GET /api/v1/opportunities/?completion_status=open
GET /api/v1/opportunities/?completion_status=solved
```

**Get Completion Statistics:**
```bash
GET /api/v1/analytics/completion-stats
```

Returns:
```json
{
  "total_opportunities": 156,
  "completion_breakdown": {
    "open": 120,
    "in_progress": 18,
    "solved": 15,
    "abandoned": 3
  },
  "completion_rate": 9.62,
  "recently_solved_count": 5,
  "recently_solved": [
    {
      "id": 23,
      "title": "Subscription management is a nightmare",
      "solved_by": "Truebill",
      "solved_at": "2024-12-01T..."
    }
  ]
}
```

---

## 🎯 Complete API Reference

### Analytics Endpoints

#### POST /api/v1/analytics/check-duplicate
Check if similar opportunity exists
- **Body**: `{title: string, description: string}`
- **Returns**: List of potential duplicates with similarity scores

#### GET /api/v1/analytics/geographic/by-scope
Filter opportunities by geographic scope
- **Params**: `scope` (local/regional/national/international/online), `limit`
- **Returns**: List of opportunities

#### GET /api/v1/analytics/geographic/by-location
Filter by specific location
- **Params**: `country`, `region`, `city`, `limit`
- **Returns**: List of opportunities

#### GET /api/v1/analytics/feasibility/{id}
Get detailed feasibility analysis
- **Returns**: Score, level, recommendation, metrics

#### GET /api/v1/analytics/top-feasible
Get highest-scoring opportunities
- **Params**: `limit`, `min_score`
- **Returns**: Ranked list of feasible opportunities

#### GET /api/v1/analytics/completion-stats
Get completion statistics
- **Returns**: Breakdown of statuses, completion rate, recent solutions

#### GET /api/v1/analytics/geographic/distribution
Get distribution by location
- **Returns**: Scope distribution, top countries

### Enhanced Opportunities Endpoints

#### GET /api/v1/opportunities/
Now supports additional filters:
- `geographic_scope` - Filter by scope
- `country` - Filter by country name
- `completion_status` - Filter by status
- `sort_by=feasibility` - Sort by feasibility score

---

## 💡 Use Cases

### For Founders
```bash
# Find high-feasibility problems in your domain
GET /api/v1/analytics/top-feasible?min_score=70
GET /api/v1/opportunities/?category=Technology&sort_by=feasibility

# Check if your idea already exists
POST /api/v1/analytics/check-duplicate
{
  "title": "Your idea here",
  "description": "Detailed description"
}
```

### For Investors
```bash
# Find validated opportunities with growth
GET /api/v1/analytics/top-feasible?limit=20

# Track which problems are being solved
GET /api/v1/analytics/completion-stats

# Geographic market analysis
GET /api/v1/analytics/geographic/distribution
```

### For Researchers
```bash
# Analyze problem distribution
GET /api/v1/analytics/geographic/distribution

# Track solution trends
GET /api/v1/opportunities/?completion_status=solved

# Identify emerging needs
GET /api/v1/opportunities/?sort_by=trending&completion_status=open
```

### For Location-Specific Businesses
```bash
# Find local opportunities
GET /api/v1/analytics/geographic/by-scope?scope=local

# Find problems in your city
GET /api/v1/analytics/geographic/by-location?city=San+Francisco

# National opportunities
GET /api/v1/analytics/geographic/by-scope?scope=national&country=United+States
```

---

## 🔧 Frontend Integration

### JavaScript Examples

```javascript
// Check for duplicates before submission
async function checkDuplicate(title, description) {
  const response = await fetch('/api/v1/analytics/check-duplicate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title, description})
  });
  const data = await response.json();

  if (data.is_duplicate) {
    // Show existing opportunities to user
    showDuplicates(data.potential_duplicates);
  }
}

// Get feasibility score
async function getFeasibility(opportunityId) {
  const response = await fetch(`/api/v1/analytics/feasibility/${opportunityId}`);
  const data = await response.json();

  return {
    score: data.feasibility_score,
    level: data.feasibility_level,
    recommendation: data.recommendation
  };
}

// Filter by location
async function getLocalOpportunities(city) {
  const params = new URLSearchParams({
    geographic_scope: 'local',
    city: city,
    limit: 20
  });

  const response = await fetch(`/api/v1/analytics/geographic/by-location?${params}`);
  return await response.json();
}

// Get top feasible opportunities
async function getTopOpportunities() {
  const response = await fetch('/api/v1/analytics/top-feasible?min_score=60&limit=10');
  return await response.json();
}
```

---

## 📈 Dashboard Ideas

### Feasibility Dashboard
```javascript
// Show top 10 most feasible opportunities
const topOpps = await fetch('/api/v1/analytics/top-feasible?limit=10');

// Display with scores, validation counts, growth rates
topOpps.forEach(opp => {
  displayOpportunity({
    title: opp.title,
    score: opp.feasibility_score,
    badge: opp.feasibility_score >= 75 ? 'High' : 'Medium'
  });
});
```

### Geographic Heatmap
```javascript
// Get distribution data
const geoData = await fetch('/api/v1/analytics/geographic/distribution');

// Visualize on map
createHeatmap(geoData.top_countries);
```

### Completion Tracker
```javascript
// Get stats
const stats = await fetch('/api/v1/analytics/completion-stats');

// Show progress
displayProgress({
  total: stats.total_opportunities,
  solved: stats.completion_breakdown.solved,
  rate: stats.completion_rate
});

// Show recent solutions
stats.recently_solved.forEach(solution => {
  displaySolution(solution);
});
```

---

## 🎨 UI Components

### Duplicate Warning
```html
<!-- Show when checking duplicates -->
<div class="duplicate-warning">
  <h3>⚠️ Similar opportunities found</h3>
  <p>These existing problems are very similar to yours:</p>

  <div class="duplicate-item">
    <h4>Finding parking in the city (78% similar)</h4>
    <p>445 validations • Growing 18.9%</p>
    <button onclick="validateExisting(5)">Validate This Instead</button>
  </div>

  <button onclick="submitAnyway()">My Problem is Different</button>
</div>
```

### Feasibility Badge
```html
<!-- Show on opportunity cards -->
<div class="opportunity-card">
  <h3>Subscription management is a nightmare</h3>

  <div class="feasibility-badge high">
    <span class="score">82.5</span>
    <span class="label">High Feasibility</span>
  </div>

  <p>312 validations • $100M-$500M market</p>
</div>
```

### Geographic Filter
```html
<!-- Filter UI -->
<select id="geoScope">
  <option value="">All Locations</option>
  <option value="local">Local</option>
  <option value="regional">Regional</option>
  <option value="national">National</option>
  <option value="international">International</option>
  <option value="online">Online</option>
</select>

<input type="text" placeholder="Country" id="country">
<input type="text" placeholder="City" id="city">
```

---

## 🧪 Testing

### Test the Features

1. **Start your backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

2. **Visit:** http://localhost:8000/docs

3. **Test scenarios:**

**Duplicate Detection:**
- Click POST `/analytics/check-duplicate`
- Try: `{"title": "parking problems", "description": "can't find parking"}`
- Should return the parking opportunity as duplicate

**Feasibility Analysis:**
- Click GET `/analytics/feasibility/5`
- See the complete scoring breakdown

**Geographic Filtering:**
- Click GET `/analytics/geographic/by-scope?scope=local`
- See only local opportunities

**Top Feasible:**
- Click GET `/analytics/top-feasible`
- See ranked opportunities by score

---

## 📝 Next Steps

1. ✅ **Initialize Database** - Run `python backend/init_db.py`
2. ✅ **Test Endpoints** - Use /docs to try features
3. 🔄 **Update Frontend** - Add geographic filters to UI
4. 🔄 **Add Visualizations** - Create feasibility dashboard
5. 🔄 **Configure Scrapers** - POST data with geographic info

---

## 💬 Support

Questions about these features? Check:
- **API Docs**: http://localhost:8000/docs
- **Main Guide**: README_SETUP.md
- **Supabase Guide**: SUPABASE_SETUP.md

Enjoy building with Friction! 🚀
