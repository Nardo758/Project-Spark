# OppGrid Census + Report Framework Specification

## Census Bureau Data Integration

### Primary Dataset: ACS 5-Year Data
- **API:** https://api.census.gov/data/2023/acs/acs5
- **Geographic Granularity:** Down to block-group level (smallest available)
- **Variables:** 20,000+ covering demographics, economics, housing

### Key ACS Variables to Integrate

```
DEMOGRAPHICS & MARKET SIZE
- B01003_001E: Total population
- B01002_001E: Median age
- B19013_001E: Median household income
- B19301_001E: Per capita income
- B17001_002E: Population below poverty line

ECONOMIC INDICATORS
- B23025_005E: Unemployment count
- B23025_002E: Labor force (for unemployment rate calc)
- B08301_*: Commute modes (car, transit, bike, walk)
- B25077_001E: Median home value
- B25064_001E: Median gross rent

HOUSEHOLD COMPOSITION
- B11001_001E: Total households
- B11001_003E: Family households
- B11001_007E: Households with children
- B09019_002E: Households with young children (under 6)

EDUCATION
- B15003_022E: Bachelor's degree
- B15003_023E: Master's degree
- B15003_024E: Professional degree
- B15003_025E: Doctorate degree
- B14007_*: School enrollment by age

CONSUMER BEHAVIOR PROXIES
- B08134_*: Commute time (indicates time poverty)
- B08301_019E: Work from home
- B28002_*: Internet access (digital adoption)
- B25044_*: Vehicle availability
```

### API Integration Example (Python)

```python
async def fetch_acs_demographics(zip_code: str, year: int = 2023) -> dict:
    base_url = 'https://api.census.gov/data'
    dataset = f'{year}/acs/acs5'
    
    variables = [
        'B01003_001E',  # Total population
        'B19013_001E',  # Median household income
        'B01002_001E',  # Median age
        'B11001_001E',  # Total households
        'B17001_002E',  # Below poverty
        'B23025_005E',  # Unemployed
        'B23025_002E',  # Labor force
        'B25077_001E',  # Median home value
        'B25064_001E',  # Median rent
        'B15003_022E',  # Bachelor's
        'B15003_023E',  # Master's
        'B15003_024E',  # Professional
        'B15003_025E',  # Doctorate
        'B08301_019E',  # Work from home
    ]
    
    url = f"{base_url}/{dataset}?get={','.join(variables)}&for=zip%20code%20tabulation%20area:{zip_code}&key={CENSUS_API_KEY}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### Database Schema

```sql
ALTER TABLE opportunities ADD COLUMN demographics JSONB;
ALTER TABLE opportunities ADD COLUMN search_trends JSONB;

-- Demographics JSONB structure:
{
  "population": 125000,
  "median_income": 78500,
  "median_age": 34.2,
  "households": 48000,
  "poverty_rate": 8.5,
  "unemployment_rate": 4.2,
  "median_home_value": 425000,
  "median_rent": 1850,
  "bachelors_or_higher_pct": 42.5,
  "work_from_home_pct": 18.3,
  "fetched_at": "2024-12-25T00:00:00Z",
  "geography_type": "zcta",
  "geography_id": "90210"
}
```

### Enhanced Signal Scoring Algorithm

```python
def calculate_enhanced_signal_score(opportunity):
    base_score = opportunity.signal_quality_score
    demographics = opportunity.demographics

    # Adjust score based on market size
    population_multiplier = min(demographics['population'] / 50000, 2.0)

    # Adjust for purchasing power
    income_multiplier = demographics['median_income'] / 75000

    # Adjust for underserved indicators
    if demographics['poverty_rate'] > 15 or demographics['unemployment_rate'] > 8:
        underserved_bonus = 1.2
    else:
        underserved_bonus = 1.0

    enhanced_score = (base_score * population_multiplier *
                     income_multiplier * underserved_bonus)

    return min(enhanced_score, 100)
```

---

## Google Trends Integration (via SerpAPI)

### Geographic Resolution
- **Available:** Country, State, DMA (Metro), City
- **NOT available:** Zipcode level
- **Strategy:** Map zipcodes → DMA codes, then query by DMA

### DMA Mapping
Use zipcode-to-DMA mapping dataset to convert opportunity locations to DMA codes for trend queries.

### Data Points
- Search interest over time
- Related queries
- Rising topics
- Regional breakdown

---

## Report Framework

### Layer 1: Problem Overview
- **Goal:** "Should I pursue this?"
- **Length:** 2-3 pages
- **Access:** $15 one-time OR included in Pro+
- **Delivery:** Web view + PDF export

**Template Sections:**
1. Executive Summary (3-4 sentences)
2. The Problem
   - What People Are Saying (3-5 curated quotes)
   - Why This Matters Now (trend catalyst, market timing, urgency indicators)
3. Market Snapshot
   - Target Customer Profile (age, income, education, location)
   - Household Characteristics (family structure, employment, commute)
   - Geographic Heat (Top 5 cities by problem density)
   - Market Size Indicators (addressable population, target households, spending power)
4. Validation Signals
   - Source Diversity
   - Problem Severity
   - Monetization Mentions
   - Competitive Gap
5. What's Next (upsell to Layer 2)
6. Sources (preview of first 3-5)

**Census Data Required:**
- B01003_001E: Total population
- B01002_001E: Median age
- B19013_001E: Median household income
- B15003_*: Educational attainment
- B11001_*: Household composition
- B23025_*: Employment status
- B25077_001E: Median home value
- B25064_001E: Median rent
- B08301_019E: Work from home

---

### Layer 2: Deep Dive Analysis
- **Goal:** "How do I pursue this?"
- **Length:** 8-12 pages
- **Access:** Business tier+
- **Delivery:** Interactive web dashboard + comprehensive PDF

**Template Sections:**
1. Market Sizing (TAM/SAM/SOM)
   - National Market Size with Census validation
   - Market Breakdown by Census Regions (Northeast, South, Midwest, West)
   - Launch Market Analysis with full demographic overlay
2. Demographic Deep Dive
   - Age distribution charts
   - Income segmentation
   - Education levels
   - Household composition
3. Competitive Landscape
   - Existing solutions
   - Market positioning map
   - Gap analysis
4. Geographic Analysis
   - 6 market breakdowns with demographic overlays
   - Heat maps of problem density
   - Regional opportunity scores
5. Customer Acquisition Channels
   - Digital adoption rates (from B28002)
   - Commute patterns (B08301)
   - Media consumption indicators
6. Financial Feasibility
   - Purchasing power analysis
   - Price sensitivity indicators
   - Revenue projections

**TAM/SAM/SOM Calculation:**
```
TAM = Target Households × Avg Annual Spending × Market Penetration
SAM = TAM × Geographic Coverage (e.g., 65% for top 50 metros)
SOM = SAM × Year 1 Market Penetration (e.g., 1%)
```

---

### Layer 3: Execution Package
- **Goal:** "Give me the complete execution plan"
- **Length:** 25-35 pages
- **Access:** Business (5/month), Enterprise (unlimited)
- **Delivery:** Full PDF report + editable spreadsheets + Notion template

**Template Sections:**
1. Everything in Layer 2
2. Complete Business Plan Template
   - Mission/Vision statements
   - Value proposition canvas
   - Business model canvas
3. Go-to-Market Strategy
   - Launch market prioritization
   - Channel strategy
   - Partnership opportunities
4. Financial Projections
   - 3-year revenue model (spreadsheet)
   - Unit economics
   - Funding requirements
5. Competitive Intelligence
   - Competitor profiles
   - SWOT analysis
   - Differentiation strategy
6. Execution Roadmap
   - 90-day launch plan
   - Key milestones
   - Resource requirements
7. Appendices
   - Full source data
   - Census data tables
   - Survey templates
   - Pitch deck outline

---

## Secondary Census Datasets (Future)

- **ACS 1-Year Data:** More current (2024), areas 65k+ population
- **Community Resilience Estimates:** Social vulnerability scores, underserved communities
- **Population Estimates API:** Most current counts, growth trends

## Data Sources NOT Needed

- Economic Census (business-focused, not consumer)
- CBP/ZBP (establishment counts)
- International Database (US-focused platform)
- Decennial Census alone (10-year old data)

---

## Competitive Advantage

> "Most competitors just count problems. OppGrid validates market size and purchasing power with official Census data at the hyperlocal level."
