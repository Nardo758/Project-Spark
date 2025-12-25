# OppGrid Enterprise API Documentation

Version: 1.0  
Last Updated: December 2024

## Overview

OppGrid provides a RESTful API for accessing opportunity intelligence, geographic data, demographic insights, and tiered reports. Enterprise customers have access to all API endpoints with higher rate limits and priority support.

## Base URL

```
Production: https://your-domain.replit.app/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

All API requests require authentication via session cookies (for web) or Bearer tokens.

### Session Authentication

The platform uses session-based authentication with Replit OAuth or email magic links. After authentication, session cookies are automatically included in requests.

### Request Headers

```http
Content-Type: application/json
Cookie: session_id=YOUR_SESSION_ID
```

---

## Opportunities API

Base path: `/api/v1/opportunities`

### List Opportunities

```http
GET /api/v1/opportunities/
```

**Query Parameters:**

| Parameter | Type    | Description                                   |
|-----------|---------|-----------------------------------------------|
| skip      | integer | Number of records to skip (default: 0)        |
| limit     | integer | Items per page (default: 20, max: 100)        |
| category  | string  | Filter by category                            |
| city      | string  | Filter by city                                |
| region    | string  | Filter by state/region                        |
| status    | string  | Filter by status (active, pending, archived)  |
| sort_by   | string  | Sort field (created_at, score, severity)      |

**Response:**

```json
{
  "opportunities": [
    {
      "id": 123,
      "title": "Mobile Pet Grooming Services",
      "category": "Home Services",
      "city": "Austin",
      "region": "TX",
      "ai_opportunity_score": 85,
      "severity": 7,
      "created_at": "2024-12-15T10:30:00Z"
    }
  ],
  "total": 1250,
  "page": 1,
  "page_size": 20
}
```

### Get Categories

```http
GET /api/v1/opportunities/categories
```

Returns list of all available opportunity categories.

### Get Opportunity Details

```http
GET /api/v1/opportunities/{opportunity_id}
```

**Response (tier-gated):**

```json
{
  "id": 123,
  "title": "Mobile Pet Grooming Services",
  "description": "Growing demand for convenient pet care...",
  "category": "Home Services",
  "city": "Austin",
  "region": "TX",
  "latitude": 30.2672,
  "longitude": -97.7431,
  "ai_opportunity_score": 85,
  "ai_market_size_estimate": "$2.5B",
  "ai_target_audience": "Pet owners aged 25-54",
  "ai_competition_level": "Medium",
  "ai_urgency_level": "High",
  "ai_business_model_suggestions": ["Mobile service", "Subscription"],
  "validation_count": 15,
  "created_at": "2024-12-15T10:30:00Z",
  "is_accessible": true,
  "access_tier": "pro"
}
```

### Get Opportunity Demographics

**Tier Required:** Business+

```http
GET /api/v1/opportunities/{opportunity_id}/demographics
```

**Response:**

```json
{
  "population": 2283371,
  "median_income": 75000,
  "median_age": 34.5,
  "total_households": 950000,
  "income_distribution": {
    "under_25k": 12.5,
    "25k_50k": 18.3,
    "50k_75k": 22.1,
    "75k_100k": 16.8,
    "100k_150k": 15.2,
    "over_150k": 15.1
  },
  "housing_tenure": {
    "owner_pct": 45.2,
    "renter_pct": 54.8
  },
  "internet_access": {
    "broadband_pct": 87.3,
    "no_internet_pct": 5.2
  },
  "data_source": "US Census Bureau ACS 5-Year Estimates"
}
```

### Get Opportunity Experts

```http
GET /api/v1/opportunities/{opportunity_id}/experts
```

Returns recommended experts for the opportunity based on category matching.

### Get Platform Stats

```http
GET /api/v1/opportunities/stats/platform
```

Returns aggregate statistics about opportunities on the platform.

### Get Featured Opportunities

```http
GET /api/v1/opportunities/featured/top
```

Returns top featured opportunities ranked by score.

---

## Map Data API

Base path: `/api/v1/map`

### Get Map Layers

```http
GET /api/v1/map/layers
```

**Response:**

```json
{
  "layers": [
    {
      "id": 1,
      "layer_name": "opportunities",
      "display_name": "Opportunity Pins",
      "layer_type": "pin",
      "is_active": true
    },
    {
      "id": 2,
      "layer_name": "heatmap",
      "display_name": "Signal Density",
      "layer_type": "heatmap",
      "is_active": true
    }
  ]
}
```

### Initialize Default Layers

```http
POST /api/v1/map/layers/initialize
```

Creates the default map layers. Returns list of created layer names.

### Get Map Data by Bounds

```http
POST /api/v1/map/data/bounds
```

**Request Body:**

```json
{
  "north": 40.9176,
  "south": 40.4774,
  "east": -73.7004,
  "west": -74.2591,
  "layers": ["opportunities", "heatmap"]
}
```

**Response:**

```json
{
  "pins": [
    {
      "id": 123,
      "latitude": 40.7128,
      "longitude": -74.0060,
      "title": "Mobile Pet Grooming",
      "category": "Home Services",
      "score": 85
    }
  ],
  "heatmap_points": [
    {"lat": 40.7128, "lng": -74.0060, "intensity": 0.85}
  ],
  "polygons": [],
  "bounds": {
    "north": 40.9176,
    "south": 40.4774,
    "east": -73.7004,
    "west": -74.2591
  }
}
```

### Get Map Data by City

```http
POST /api/v1/map/data/city
```

**Request Body:**

```json
{
  "city": "Austin",
  "state": "TX",
  "layers": ["opportunities"]
}
```

### Get Map Data by City (Simple)

```http
GET /api/v1/map/data/city/{city}?state=TX
```

Simple GET endpoint for fetching city map data.

### Get Map Statistics

```http
GET /api/v1/map/statistics
```

Returns statistics about geographic features and layer data.

### Save Map Session

```http
POST /api/v1/map/session
```

**Request Body:**

```json
{
  "layer_state": {"opportunities": true, "heatmap": false},
  "viewport": {"center": [-97.7431, 30.2672], "zoom": 10},
  "session_name": "Austin Analysis"
}
```

### Get User Map Sessions

```http
GET /api/v1/map/sessions?limit=10
```

Returns user's saved map sessions.

### Get Opportunity Map Data

**Tier Required:** Pro+

```http
GET /api/v1/map/opportunity/{opportunity_id}
```

Returns geographic data specific to an opportunity including service area and demographic overlays.

### Get Growth Trajectories

**Tier Required:** Business+

```http
GET /api/v1/map/growth-trajectories?state=48
```

**Query Parameters:**

| Parameter | Type   | Description                              |
|-----------|--------|------------------------------------------|
| state     | string | Filter by state FIPS code                |
| category  | string | Growth category (high, moderate, stable) |

**Response:**

```json
{
  "trajectories": [
    {
      "id": 1,
      "city": "Austin",
      "state_fips": "48",
      "geography_name": "Travis County",
      "growth_category": "high",
      "growth_score": 92.5,
      "population_growth_rate": 2.8,
      "net_migration_rate": 1.5,
      "latitude": 30.2672,
      "longitude": -97.7431
    }
  ]
}
```

### Get Migration Flows

**Tier Required:** Enterprise

```http
GET /api/v1/map/migration-flows?origin=06&destination=48
```

**Query Parameters:**

| Parameter  | Type    | Description               |
|------------|---------|---------------------------|
| origin     | string  | Origin state FIPS code    |
| destination| string  | Destination state FIPS    |
| min_flow   | integer | Minimum migration count   |

**Response:**

```json
{
  "flows": [
    {
      "origin_name": "California",
      "origin_state_fips": "06",
      "destination_name": "Texas",
      "destination_state_fips": "48",
      "flow_count": 82235,
      "year": 2022
    }
  ]
}
```

---

## Reports API

Base path: `/api/v1/reports`

### List User Reports

```http
GET /api/v1/reports/
```

**Query Parameters:**

| Parameter      | Type    | Description                         |
|----------------|---------|-------------------------------------|
| page           | integer | Page number (default: 1)            |
| page_size      | integer | Items per page (default: 20)        |
| report_type    | string  | Filter by type (LAYER_1_OVERVIEW, etc.) |
| status         | string  | Filter by status (pending, completed) |
| opportunity_id | integer | Filter by opportunity               |

**Response:**

```json
{
  "reports": [
    {
      "id": 456,
      "report_type": "LAYER_1_OVERVIEW",
      "title": "Problem Overview: Mobile Pet Grooming",
      "status": "completed",
      "opportunity_id": 123,
      "created_at": "2024-12-25T14:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20
}
```

### Get User Report Stats

```http
GET /api/v1/reports/my-stats
```

Returns current user's report generation statistics.

### Get Report Details

```http
GET /api/v1/reports/{report_id}
```

Returns full report content and metadata.

### Generate Layer 1 Report

**Tier Required:** Pro+ (or $15 pay-per-unlock)

```http
POST /api/v1/reports/opportunity/{opportunity_id}/layer1
```

Generates a Problem Overview report including:
- Executive Summary
- Problem Statement
- Market Snapshot with static map
- Validation Signals
- Key Risks
- Recommended Next Steps

**Response:**

```json
{
  "id": 456,
  "report_type": "LAYER_1_OVERVIEW",
  "title": "Problem Overview: Mobile Pet Grooming",
  "status": "completed",
  "content": "<html>...</html>",
  "summary": "Brief executive summary...",
  "confidence_score": 85,
  "generation_time_ms": 1250,
  "completed_at": "2024-12-25T14:30:00Z"
}
```

### Generate Layer 2 Report

**Tier Required:** Business+

```http
POST /api/v1/reports/opportunity/{opportunity_id}/layer2
```

Generates Deep Dive Analysis adding to Layer 1:
- TAM/SAM/SOM Analysis
- Demographic Deep Dive (Census data)
- Income Distribution
- Housing & Lifestyle Patterns
- Top 10 Markets by Score
- Competitive Landscape
- Geographic Analysis with static map

### Generate Layer 3 Report

**Tier Required:** Business (5/month limit) or Enterprise (unlimited)

```http
POST /api/v1/reports/opportunity/{opportunity_id}/layer3
```

Generates Full Execution Package including:
- Complete Business Plan
- Go-to-Market Strategy (3 phases)
- Financial Projections (3-year)
- 90-Day Execution Roadmap
- Risk Mitigation Plan
- Expert Recommendations

---

## Admin API

Base path: `/api/v1/admin`

**Access Required:** Admin user authentication

### Map Usage Statistics

```http
GET /api/v1/admin/map-usage/stats?days=30
```

**Query Parameters:**

| Parameter | Type    | Description                          |
|-----------|---------|--------------------------------------|
| days      | integer | Lookback period (1-365, default: 30) |

**Response:**

```json
{
  "total_sessions": 15420,
  "recent_sessions": 3250,
  "unique_users": 890,
  "growth_trajectories": 245,
  "migration_flows": 1250,
  "service_areas": 450,
  "layer_usage": {
    "opportunities": 2800,
    "heatmap": 1950,
    "growth_markets": 1200
  },
  "daily_sessions": [
    {"date": "2024-12-24 00:00:00", "count": 125},
    {"date": "2024-12-25 00:00:00", "count": 98}
  ],
  "period_days": 30
}
```

### Popular Opportunities by Map Usage

```http
GET /api/v1/admin/map-usage/popular-opportunities?limit=10
```

**Query Parameters:**

| Parameter | Type    | Description            |
|-----------|---------|------------------------|
| limit     | integer | Max results (1-50)     |

**Response:**

```json
{
  "opportunities": [
    {
      "opportunity_id": 123,
      "title": "Mobile Pet Grooming",
      "category": "Home Services",
      "signal_count": 45,
      "total_population": 2500000,
      "addressable_market": 125000000
    }
  ]
}
```

### Growth Trajectories Admin View

```http
GET /api/v1/admin/map-usage/growth-trajectories
```

Returns all active growth trajectory data ordered by growth score.

### Migration Flows Admin View

```http
GET /api/v1/admin/map-usage/migration-flows?limit=50
```

Returns top migration flows by flow count.

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Description                                    |
|------|------------------------------------------------|
| 200  | Success                                        |
| 201  | Created                                        |
| 400  | Bad Request - Invalid parameters               |
| 401  | Unauthorized - Missing or invalid auth         |
| 403  | Forbidden - Insufficient tier access           |
| 404  | Not Found - Resource doesn't exist             |
| 422  | Unprocessable Entity - Validation failed       |
| 500  | Internal Server Error                          |

---

## Tier Access Summary

| Feature                    | Free | Pro | Business | Enterprise |
|----------------------------|------|-----|----------|------------|
| List Opportunities         | Yes  | Yes | Yes      | Yes        |
| View Opportunity Details   | Limited | Full | Full  | Full       |
| Demographics Data          | No   | No  | Yes      | Yes        |
| Layer 1 Reports            | $15  | Yes | Yes      | Yes        |
| Layer 2 Reports            | No   | No  | Yes      | Yes        |
| Layer 3 Reports            | No   | No  | 5/month  | Unlimited  |
| Interactive Map            | Preview | Full | Full  | Full       |
| Growth Trajectories        | No   | No  | Yes      | Yes        |
| Migration Flows            | No   | No  | No       | Yes        |
| Admin Analytics            | No   | No  | No       | Yes        |

---

## API Integration Examples

### Python (requests)

```python
import requests

BASE_URL = "https://your-domain.replit.app/api/v1"

# List opportunities
response = requests.get(
    f"{BASE_URL}/opportunities/",
    params={"category": "Home Services", "page_size": 20},
    cookies={"session_id": "YOUR_SESSION_ID"}
)
opportunities = response.json()

# Get demographics (Business+ tier)
response = requests.get(
    f"{BASE_URL}/opportunities/123/demographics",
    cookies={"session_id": "YOUR_SESSION_ID"}
)
demographics = response.json()

# Generate Layer 1 report
response = requests.post(
    f"{BASE_URL}/reports/opportunity/123/layer1",
    cookies={"session_id": "YOUR_SESSION_ID"}
)
report = response.json()
```

### JavaScript (fetch)

```javascript
const BASE_URL = 'https://your-domain.replit.app/api/v1';

// List opportunities
const oppsResponse = await fetch(`${BASE_URL}/opportunities/?category=Home+Services`, {
  credentials: 'include'
});
const opportunities = await oppsResponse.json();

// Get map data by city
const mapResponse = await fetch(`${BASE_URL}/map/data/city`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    city: 'Austin',
    state: 'TX',
    layers: ['opportunities']
  })
});
const mapData = await mapResponse.json();
```

---

## OpenAPI Documentation

The full OpenAPI specification is available at:

```
/api/v1/docs     - Swagger UI
/api/v1/redoc    - ReDoc UI
/api/v1/openapi.json - Raw OpenAPI spec
```

---

## Support

For questions or issues:
- Check the OpenAPI documentation for detailed request/response schemas
- Contact support through the platform dashboard
