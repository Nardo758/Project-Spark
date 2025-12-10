# 🎨 Frontend Integration Guide

## ✅ What's Been Integrated

Your Friction frontend is now fully connected to the backend API with all advanced features!

### New Files Created
- **`js/app.js`** - Main application logic with API integration
- **`js/api.js`** - API client library (already created)
- **`css/features.css`** - Styles for new features

### Updated Files
- **`index.html`** - Added script and CSS references

---

## 🚀 How to Use

### 1. Start Your Backend
```bash
cd backend
uvicorn app.main:app --reload
```

Backend will run at: **http://localhost:8000**

### 2. Serve the Frontend
```bash
# Option 1: Python HTTP Server
python3 -m http.server 5500

# Option 2: VS Code Live Server
# Right-click index.html → "Open with Live Server"

# Option 3: Node.js
npx http-server -p 5500
```

Frontend will run at: **http://localhost:5500**

### 3. Open in Browser
Visit: **http://localhost:5500/index.html**

---

## 🎯 Features Now Available

### 1. **Real-Time Opportunity Loading**
- Opportunities load from your Supabase database
- Automatic refresh on filters
- Pagination support

### 2. **Feasibility Scores**
Every opportunity shows:
- **Score badge** (0-100)
- **Color-coded level** (High/Medium/Low/Very Low)
- Click for detailed analysis

### 3. **Geographic Filters**
Filter opportunities by:
- **Scope**: Local, Regional, National, International, Online
- **Country**: Type to search
- **Category**: Problem type
- **Completion Status**: Open, In Progress, Solved, Abandoned

### 4. **Duplicate Detection**
When submitting new opportunities:
- Automatically checks for similar problems
- Shows similarity percentage
- Option to validate existing instead

### 5. **Sorting Options**
Sort by:
- **Recent** - Newest first
- **Trending** - Highest growth rate
- **Validated** - Most validations
- **Market** - Largest market size
- **Feasibility** - Highest score

### 6. **Top Feasible Dashboard**
See the 10 most feasible opportunities with:
- Ranking (#1-10)
- Feasibility scores
- Validation counts
- Growth metrics

### 7. **Geographic Distribution**
Visual breakdown of:
- Opportunities by scope
- Top countries
- Distribution charts

### 8. **Completion Statistics**
Track progress:
- Completion rate percentage
- Status breakdown
- Recently solved problems
- Who solved them

---

## 🔧 Adding Features to Your Pages

### Load Opportunities on Page Load
```javascript
// In your page's JavaScript
document.addEventListener('DOMContentLoaded', async () => {
    await FrictionApp.loadOpportunities();
});
```

### Add Filter Controls
```html
<div class="filters-container">
    <div class="filters-row">
        <div class="filter-group">
            <label>Geographic Scope</label>
            <select id="geo-scope-filter">
                <option value="">All Locations</option>
                <option value="local">Local</option>
                <option value="regional">Regional</option>
                <option value="national">National</option>
                <option value="international">International</option>
                <option value="online">Online</option>
            </select>
        </div>

        <div class="filter-group">
            <label>Country</label>
            <input type="text" id="country-filter" placeholder="e.g., United States">
        </div>

        <div class="filter-group">
            <label>Sort By</label>
            <select id="sort-filter">
                <option value="recent">Most Recent</option>
                <option value="trending">Trending</option>
                <option value="validated">Most Validated</option>
                <option value="feasibility">Highest Feasibility</option>
            </select>
        </div>

        <div class="filter-group">
            <label>Status</label>
            <select id="status-filter">
                <option value="">All</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="solved">Solved</option>
            </select>
        </div>
    </div>
</div>
```

### Display Opportunities
```html
<div id="opportunities-container">
    <!-- Opportunities will load here -->
</div>
```

### Show Top Feasible
```html
<div id="top-feasible-container"></div>

<script>
    FrictionApp.loadTopFeasible();
</script>
```

### Show Geographic Distribution
```html
<div id="geo-distribution-container"></div>

<script>
    FrictionApp.loadGeographicDistribution();
</script>
```

### Show Completion Stats
```html
<div id="completion-stats-container"></div>

<script>
    FrictionApp.loadCompletionStats();
</script>
```

---

## 💡 Customization

### Change API URL
Edit `js/app.js`:
```javascript
const API_BASE_URL = 'https://your-api-domain.com/api/v1';
```

### Customize Opportunity Card
Modify `createOpportunityCard()` function in `js/app.js`:
```javascript
function createOpportunityCard(opp) {
    // Your custom card HTML
}
```

### Customize Feasibility Thresholds
Edit `getFeasibilityBadge()` in `js/app.js`:
```javascript
if (score >= 80) {  // Changed from 75
    level = 'High';
}
```

### Add Custom Filters
```javascript
async function loadMyCustomFilter() {
    await FrictionApp.loadOpportunities({
        category: 'Technology',
        geographic_scope: 'online',
        completion_status: 'open',
        min_feasibility: 60
    });
}
```

---

## 🎨 UI Components Reference

### Feasibility Badge Colors
```css
.feasibility-high     { background: #D1FAE5; color: #065F46; }  /* Green */
.feasibility-medium   { background: #FEF3C7; color: #92400E; }  /* Yellow */
.feasibility-low      { background: #FEE2E2; color: #991B1B; }  /* Red */
.feasibility-very-low { background: #F3F4F6; color: #6B7280; }  /* Gray */
```

### Geographic Badge
```html
<span class="geo-badge">
    📍 San Francisco
</span>
```

### Opportunity Card Structure
```html
<div class="opportunity-card" onclick="showOpportunityDetail(id)">
    <div class="card-header">
        <h3>Title</h3>
        <div class="feasibility-badge feasibility-high">
            <span class="score">82.5</span>
            <span class="level">High</span>
        </div>
    </div>
    <p class="description">...</p>
    <div class="card-meta">
        <span class="category">Technology</span>
        <span class="geo-badge">💻 Online</span>
        <span class="validation-count">✓ 234 validations</span>
        <span class="growth">↗ 15.3%</span>
    </div>
    <div class="card-footer">
        <span class="severity">Severity: 4/5</span>
        <span class="market-size">$50M-$100M</span>
    </div>
</div>
```

---

## 🔄 API Integration Examples

### Submit Opportunity with Duplicate Check
```javascript
const submitBtn = document.getElementById('submit-opportunity');
submitBtn.addEventListener('click', async () => {
    const formData = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        category: document.getElementById('category').value,
        severity: parseInt(document.getElementById('severity').value),
        geographic_scope: document.getElementById('geo-scope').value,
        country: document.getElementById('country').value,
        region: document.getElementById('region').value,
        city: document.getElementById('city').value
    };

    await FrictionApp.submitOpportunity(formData);
});
```

### Validate Opportunity
```javascript
async function validateOpportunity(oppId) {
    await FrictionApp.validateExisting(oppId);
}
```

### Load with Filters
```javascript
// Load local opportunities in San Francisco
await FrictionApp.loadOpportunities({
    geographic_scope: 'local',
    city: 'San Francisco'
});

// Load high-feasibility tech opportunities
await FrictionApp.loadOpportunities({
    category: 'Technology',
    sort_by: 'feasibility'
});

// Load solved opportunities
await FrictionApp.loadOpportunities({
    completion_status: 'solved'
});
```

---

## 🧪 Testing

### 1. Test Opportunity Loading
1. Open browser console (F12)
2. Run: `FrictionApp.loadOpportunities()`
3. Should see 6 opportunities from init_db.py

### 2. Test Duplicate Detection
1. Click "Submit Opportunity"
2. Enter title: "parking problems"
3. Should show duplicate warning for existing parking opportunity

### 3. Test Filters
1. Select "Local" from geographic scope filter
2. Should show only local opportunities (handyman, gym, parking)

### 4. Test Feasibility
1. Click on any opportunity
2. Should load and display feasibility analysis

### 5. Test Top Feasible
1. Call: `FrictionApp.loadTopFeasible()`
2. Should show ranked list of opportunities

---

## 🐛 Troubleshooting

### Opportunities Not Loading
**Check:**
1. Is backend running? Visit http://localhost:8000/docs
2. Check browser console for CORS errors
3. Verify API_BASE_URL in js/app.js matches your backend

**Fix CORS:**
Update `backend/.env`:
```env
BACKEND_CORS_ORIGINS=["http://localhost:5500","http://127.0.0.1:5500"]
```

Restart backend after changing.

### 404 Errors on Scripts
**Check file paths:**
```html
<script src="js/api.js"></script>  <!-- Correct -->
<script src="/js/api.js"></script> <!-- May fail on some servers -->
```

### Authentication Not Working
**Check:**
1. Token is being stored: `localStorage.getItem('access_token')`
2. Login redirects properly
3. API returns valid token

---

## 📊 Analytics Dashboard Example

Create a full analytics page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Friction Analytics</title>
    <link rel="stylesheet" href="css/features.css">
</head>
<body>
    <div class="container">
        <h1>📊 Analytics Dashboard</h1>

        <!-- Top Feasible -->
        <section>
            <div id="top-feasible-container"></div>
        </section>

        <!-- Geographic Distribution -->
        <section>
            <div id="geo-distribution-container"></div>
        </section>

        <!-- Completion Stats -->
        <section>
            <div id="completion-stats-container"></div>
        </section>
    </div>

    <script src="js/api.js"></script>
    <script src="js/app.js"></script>
    <script>
        // Load all analytics
        document.addEventListener('DOMContentLoaded', () => {
            FrictionApp.loadTopFeasible();
            FrictionApp.loadGeographicDistribution();
            FrictionApp.loadCompletionStats();
        });
    </script>
</body>
</html>
```

---

## 🎯 Next Steps

1. ✅ **Backend is running** - `uvicorn app.main:app --reload`
2. ✅ **Frontend is integrated** - Open http://localhost:5500
3. 🔄 **Test all features** - Filters, submission, validation
4. 🔄 **Customize UI** - Match your design preferences
5. 🔄 **Add more pages** - Analytics, user dashboard, etc.
6. 🔄 **Configure scrapers** - POST data to API endpoints

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Features Guide**: FEATURES_GUIDE.md
- **Backend Setup**: QUICKSTART_SUPABASE.md
- **Main README**: README.md

---

**Your frontend is now fully integrated with all backend features!** 🎉

Start your backend, open the frontend, and start testing! All the advanced features (geographic tracking, duplicate detection, feasibility analysis, completion tracking) are ready to use.
