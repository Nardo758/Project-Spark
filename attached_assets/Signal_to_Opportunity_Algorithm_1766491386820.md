# Signal-to-Opportunity Conversion Algorithm

**Transform raw scraped signals into validated, location-mapped business opportunities**

---

## 📋 Table of Contents

1. [Algorithm Overview](#algorithm-overview)
2. [Processing Pipeline](#processing-pipeline)
3. [Signal Aggregation](#signal-aggregation)
4. [Business Idea Extraction](#business-idea-extraction)
5. [Location Validation & Mapping](#location-validation--mapping)
6. [Opportunity Validation](#opportunity-validation)
7. [Deduplication & Merging](#deduplication--merging)
8. [Market Sizing](#market-sizing)
9. [Output Format](#output-format)
10. [Implementation Examples](#implementation-examples)

---

## 1. Algorithm Overview

### High-Level Flow

```
Raw Scraped Data (Reddit, Yelp, etc.)
    ↓
[1] Pattern Matching & Scoring (keyword_matrix.py)
    ↓
[2] Signal Aggregation (cluster similar problems)
    ↓
[3] Business Idea Extraction (what to build)
    ↓
[4] Location Validation (where the demand is)
    ↓
[5] Opportunity Validation (confidence scoring)
    ↓
[6] Deduplication & Merging (combine duplicates)
    ↓
[7] Market Sizing (estimate opportunity size)
    ↓
Validated Business Opportunity (ready for database)
```

### Goal
Convert **100 raw signals** into **10-15 validated, unique business opportunities** with:
- Clear business idea (what to build)
- Validated demand (confidence score)
- Geographic location (city, state, coverage area)
- Market size estimate

---

## 2. Processing Pipeline

### Stage 1: Raw Signal Collection

**Input:** Scraped data from all 9 sources

```python
raw_signal = {
    'source': 'reddit',
    'id': 'abc123',
    'title': 'I wish there was parking app in SF',
    'text': 'Can\'t find parking anywhere in Mission. Would pay $50/month.',
    'author': 'user123',
    'url': 'https://reddit.com/...',
    'scraped_at': '2024-01-15T10:30:00Z',
    'metadata': {...}
}
```

**Stage 1 Output:** Raw signals with basic metadata

---

### Stage 2: Pattern Matching & Initial Scoring

**Process:** Apply keyword_matrix.py patterns

```python
from keyword_matrix import (
    BUSINESS_IDEA_KEYWORDS,
    LOCATION_KEYWORDS,
    calculate_composite_score
)

# Detect patterns
patterns_found = []
for category, data in BUSINESS_IDEA_KEYWORDS.items():
    if matches_pattern(signal['text'], data['patterns']):
        patterns_found.append({
            'category': category,
            'confidence': data['confidence']
        })

# Extract location
location = extract_location(signal)

# Calculate score
score = calculate_composite_score({
    'patterns': patterns_found,
    'location_confidence': location['confidence'],
    'source': signal['source']
})
```

**Stage 2 Output:** Signals with scores (filter out < 0.70)

---

### Stage 3: Signal Aggregation (Clustering)

**Problem:** 100 signals might describe the same opportunity

**Example Cluster:**
- Signal 1: "Need parking near Caltrain in SF"
- Signal 2: "Wish there was parking app in Mission"
- Signal 3: "Can't find parking downtown SF"

**Solution:** Group by:
1. **Problem type** (parking, childcare, etc.)
2. **Location** (San Francisco, CA)
3. **Time window** (within 30 days)

**Stage 3 Output:** Signal clusters (groups of related problems)

---

### Stage 4: Business Idea Extraction

**From clustered signals, extract:**
1. Core problem statement
2. Proposed solution type
3. Key features needed
4. Target customer

**Stage 4 Output:** Structured business idea

---

### Stage 5: Location Validation & Mapping

**Process:**
1. Verify all signals have same location
2. Calculate geographic coverage area
3. Map to city, neighborhood, ZIP codes
4. Determine service radius

**Stage 5 Output:** Location-validated opportunity

---

### Stage 6: Opportunity Validation

**Apply validation rules:**
- Minimum signals: 3+
- Location confidence: ≥0.70
- Signal score: ≥0.70
- Time span: ≤60 days
- Category identified: Yes

**Stage 6 Output:** Validated opportunity with confidence tier

---

### Stage 7: Deduplication & Merging

**Check for duplicates:**
- Same problem + same location = merge
- Similar problem + nearby location = link

**Stage 7 Output:** Unique opportunities

---

### Stage 8: Market Sizing

**Estimate:**
- Potential customer count
- Geographic reach
- Competitive landscape
- Revenue potential

**Stage 8 Output:** Final business opportunity

---

## 3. Signal Aggregation

### Clustering Algorithm

**Step 1: Define Similarity Criteria**

Two signals are similar if they match on:

```python
SIMILARITY_CRITERIA = {
    'problem_category': {
        'weight': 0.40,  # Most important
        'threshold': 'exact_match'  # Must be same category
    },
    'location': {
        'weight': 0.30,
        'threshold': 'same_city_or_within_25_miles'
    },
    'problem_keywords': {
        'weight': 0.20,
        'threshold': '3+_shared_keywords'
    },
    'time_proximity': {
        'weight': 0.10,
        'threshold': 'within_30_days'
    }
}
```

**Step 2: Calculate Similarity Score**

```python
def calculate_similarity(signal_a, signal_b):
    """Calculate similarity between two signals"""
    
    similarity = 0.0
    
    # Category match (40%)
    if signal_a['category'] == signal_b['category']:
        similarity += 0.40
    
    # Location match (30%)
    if signal_a['city'] == signal_b['city']:
        similarity += 0.30
    elif distance_miles(signal_a, signal_b) <= 25:
        similarity += 0.15
    
    # Keyword overlap (20%)
    shared_keywords = set(signal_a['keywords']) & set(signal_b['keywords'])
    keyword_similarity = len(shared_keywords) / max(
        len(signal_a['keywords']),
        len(signal_b['keywords'])
    )
    similarity += 0.20 * keyword_similarity
    
    # Time proximity (10%)
    days_apart = abs((signal_a['date'] - signal_b['date']).days)
    if days_apart <= 30:
        time_score = 1.0 - (days_apart / 30)
        similarity += 0.10 * time_score
    
    return similarity

# Threshold: similarity >= 0.65 = same cluster
```

**Step 3: Form Clusters**

```python
def cluster_signals(signals):
    """Group similar signals into clusters"""
    
    clusters = []
    processed = set()
    
    for i, signal_a in enumerate(signals):
        if signal_a['id'] in processed:
            continue
        
        # Start new cluster
        cluster = [signal_a]
        processed.add(signal_a['id'])
        
        # Find similar signals
        for j, signal_b in enumerate(signals):
            if i != j and signal_b['id'] not in processed:
                similarity = calculate_similarity(signal_a, signal_b)
                
                if similarity >= 0.65:
                    cluster.append(signal_b)
                    processed.add(signal_b['id'])
        
        clusters.append(cluster)
    
    return clusters
```

**Example Cluster:**

```python
cluster_1 = [
    {
        'id': 'reddit_abc',
        'text': 'Need parking near Caltrain SF',
        'category': 'transportation',
        'city': 'San Francisco',
        'score': 0.90
    },
    {
        'id': 'craigslist_def',
        'text': 'Wanted: parking spot Mission District $300/mo',
        'category': 'transportation',
        'city': 'San Francisco',
        'score': 0.95
    },
    {
        'id': 'twitter_ghi',
        'text': 'Why is SF parking so expensive downtown?',
        'category': 'transportation',
        'city': 'San Francisco',
        'score': 0.75
    }
]
# Result: 3 signals → 1 opportunity cluster
```

---

## 4. Business Idea Extraction

### Extract Core Problem

**Algorithm:**

```python
def extract_core_problem(cluster):
    """Extract the core problem from signal cluster"""
    
    # Step 1: Aggregate all problem statements
    all_text = ' '.join([s['text'] for s in cluster])
    
    # Step 2: Extract most frequent nouns/phrases
    from collections import Counter
    
    keywords = extract_keywords(all_text)
    keyword_freq = Counter(keywords)
    top_keywords = keyword_freq.most_common(10)
    
    # Step 3: Identify problem pattern
    problem_patterns = []
    for signal in cluster:
        for pattern_cat, pattern_data in BUSINESS_IDEA_KEYWORDS.items():
            for pattern in pattern_data['patterns']:
                if re.search(pattern, signal['text'], re.IGNORECASE):
                    problem_patterns.append({
                        'pattern': pattern,
                        'category': pattern_cat,
                        'text': signal['text']
                    })
    
    # Step 4: Generate problem statement
    category = cluster[0]['category']  # All should be same
    location = cluster[0]['city']
    primary_keyword = top_keywords[0][0]  # Most frequent keyword
    
    core_problem = {
        'category': category,
        'primary_keyword': primary_keyword,
        'location': location,
        'problem_statement': generate_problem_statement(
            category, primary_keyword, location, problem_patterns
        ),
        'raw_signals': [s['text'] for s in cluster]
    }
    
    return core_problem
```

**Problem Statement Templates:**

```python
PROBLEM_TEMPLATES = {
    'transportation': {
        'parking': "{location} residents struggle to find affordable, convenient parking near {areas}",
        'transit': "{location} lacks reliable {transit_type} connecting {areas}",
        'rideshare': "{location} needs better alternatives to {incumbent} for {use_case}"
    },
    'childcare': {
        'daycare': "Parents in {location} face {problem} finding affordable childcare in {neighborhoods}",
        'babysitter': "{location} families need reliable on-demand childcare for {time_periods}"
    },
    'home_services': {
        'general': "{location} residents can't find reliable {service_type} providers",
        'quality': "{location} needs quality-verified {service_type} with transparent pricing"
    },
    'product_marketplace': {
        'supply_gap': "{location} consumers can't find {product_type} locally",
        'quality_gap': "{location} needs higher-quality alternatives to {incumbent_product}"
    },
    'service_marketplace': {
        'provider_gap': "{location} residents struggle to find reliable {service_providers}",
        'feature_gap': "{location} needs {service_type} with {missing_feature}"
    }
}
```

### Generate Solution Concept

```python
def generate_solution_concept(core_problem, cluster):
    """Generate solution concept from problem"""
    
    solution = {
        'solution_type': None,
        'solution_statement': None,
        'key_features': [],
        'differentiation': []
    }
    
    # Determine solution type based on patterns
    demand_types = [s.get('demand_type') for s in cluster]
    
    if 'product' in demand_types:
        solution['solution_type'] = 'product'
        solution['solution_statement'] = generate_product_solution(core_problem)
        
    elif 'service' in demand_types:
        solution['solution_type'] = 'service'
        solution['solution_statement'] = generate_service_solution(core_problem)
        
    elif 'marketplace_gap' in demand_types:
        solution['solution_type'] = 'marketplace'
        solution['solution_statement'] = generate_marketplace_solution(core_problem)
    
    else:
        # Default: software solution
        solution['solution_type'] = 'software'
        solution['solution_statement'] = generate_software_solution(core_problem)
    
    # Extract key features from pain points
    solution['key_features'] = extract_key_features(cluster)
    
    # Identify differentiation
    solution['differentiation'] = extract_differentiation(cluster)
    
    return solution
```

**Example Output:**

```python
business_idea = {
    'core_problem': {
        'category': 'transportation',
        'primary_keyword': 'parking',
        'location': 'San Francisco',
        'problem_statement': 'San Francisco residents struggle to find affordable, convenient parking near transit stations and downtown'
    },
    'solution_concept': {
        'solution_type': 'software',
        'solution_statement': 'Real-time parking availability app showing open spots near transit with monthly subscription',
        'key_features': [
            'Real-time spot availability',
            'Price comparison',
            'Near transit stations',
            'Monthly parking passes',
            'Reservations'
        ],
        'differentiation': [
            'Focus on transit-adjacent parking',
            'Flat monthly rate vs hourly',
            'Guaranteed spot availability'
        ]
    }
}
```

---

## 5. Location Validation & Mapping

### Validate Location Across Cluster

```python
def validate_location(cluster):
    """Ensure consistent location across cluster"""
    
    locations = []
    
    for signal in cluster:
        if signal.get('city') and signal.get('state'):
            locations.append({
                'city': signal['city'],
                'state': signal['state'],
                'confidence': signal.get('location_confidence', 0.0),
                'lat': signal.get('latitude'),
                'lng': signal.get('longitude')
            })
    
    # Determine primary location (most common + highest confidence)
    from collections import Counter
    
    city_counts = Counter([loc['city'] for loc in locations])
    primary_city = city_counts.most_common(1)[0][0]
    
    # Filter to primary city
    city_locations = [loc for loc in locations if loc['city'] == primary_city]
    
    # Calculate average confidence
    avg_confidence = sum(loc['confidence'] for loc in city_locations) / len(city_locations)
    
    # Calculate centroid (if lat/lng available)
    lats = [loc['lat'] for loc in city_locations if loc.get('lat')]
    lngs = [loc['lng'] for loc in city_locations if loc.get('lng')]
    
    if lats and lngs:
        centroid = {
            'lat': sum(lats) / len(lats),
            'lng': sum(lngs) / len(lngs)
        }
    else:
        centroid = None
    
    return {
        'city': primary_city,
        'state': city_locations[0]['state'],
        'confidence': avg_confidence,
        'signal_count': len(city_locations),
        'centroid': centroid
    }
```

### Calculate Coverage Area

```python
def calculate_coverage_area(cluster, primary_location):
    """Calculate geographic coverage radius"""
    
    # Get all lat/lng points
    points = []
    for signal in cluster:
        if signal.get('latitude') and signal.get('longitude'):
            points.append((signal['latitude'], signal['longitude']))
    
    if len(points) < 2:
        # Default radius for single point or no coordinates
        return {
            'radius_miles': 5.0,
            'coverage_type': 'default',
            'neighborhoods': []
        }
    
    # Calculate distance from centroid to furthest point
    from math import radians, cos, sin, asin, sqrt
    
    centroid = primary_location['centroid']
    
    max_distance = 0
    for point in points:
        distance = haversine_distance(
            centroid['lat'], centroid['lng'],
            point[0], point[1]
        )
        max_distance = max(max_distance, distance)
    
    # Add 20% buffer
    coverage_radius = max_distance * 1.2
    
    # Adaptive radius based on density
    if len(points) >= 10:
        # High density = smaller, focused area
        coverage_radius = min(coverage_radius, 10.0)
    elif len(points) >= 5:
        coverage_radius = min(coverage_radius, 15.0)
    else:
        # Low density = larger area
        coverage_radius = min(coverage_radius, 25.0)
    
    # Extract neighborhoods mentioned
    neighborhoods = extract_neighborhoods(cluster)
    
    return {
        'radius_miles': round(coverage_radius, 1),
        'coverage_type': 'calculated',
        'neighborhoods': neighborhoods,
        'signal_density': len(points) / (coverage_radius ** 2)  # signals per sq mile
    }

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in miles"""
    R = 3959  # Earth radius in miles
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return R * c
```

### Map to Geographic Entities

```python
def map_to_geographic_entities(primary_location, coverage_area):
    """Map opportunity to ZIP codes, neighborhoods, districts"""
    
    # Would use geocoding API in production
    # For now, extract from signals
    
    entities = {
        'city': primary_location['city'],
        'state': primary_location['state'],
        'neighborhoods': coverage_area['neighborhoods'],
        'zip_codes': [],
        'density_type': None
    }
    
    # Determine density type
    if coverage_area['radius_miles'] <= 5:
        entities['density_type'] = 'hyperlocal'
    elif coverage_area['radius_miles'] <= 15:
        entities['density_type'] = 'city'
    else:
        entities['density_type'] = 'regional'
    
    return entities
```

**Example Output:**

```python
location_data = {
    'primary_location': {
        'city': 'San Francisco',
        'state': 'CA',
        'confidence': 0.92,
        'signal_count': 8,
        'centroid': {'lat': 37.7749, 'lng': -122.4194}
    },
    'coverage_area': {
        'radius_miles': 7.5,
        'coverage_type': 'calculated',
        'neighborhoods': ['Mission', 'SOMA', 'Downtown', 'Financial District'],
        'signal_density': 0.14
    },
    'geographic_entities': {
        'city': 'San Francisco',
        'state': 'CA',
        'neighborhoods': ['Mission', 'SOMA', 'Downtown'],
        'zip_codes': ['94103', '94110', '94105'],
        'density_type': 'city'
    }
}
```

---

## 6. Opportunity Validation

### Validation Scorecard

```python
def validate_opportunity(business_idea, cluster, location_data):
    """Apply validation rules to determine if opportunity is viable"""
    
    validation = {
        'passed': False,
        'validation_score': 0.0,
        'confidence_tier': None,
        'validation_criteria': {},
        'red_flags': [],
        'green_flags': []
    }
    
    # Criteria 1: Minimum Signal Count (weight: 20%)
    signal_count = len(cluster)
    if signal_count >= 5:
        validation['validation_criteria']['signal_count'] = 1.0
        validation['green_flags'].append(f"{signal_count} signals (strong demand)")
    elif signal_count >= 3:
        validation['validation_criteria']['signal_count'] = 0.7
    else:
        validation['validation_criteria']['signal_count'] = 0.3
        validation['red_flags'].append(f"Only {signal_count} signals (weak demand)")
    
    # Criteria 2: Average Signal Quality (weight: 25%)
    avg_score = sum(s['signal_score'] for s in cluster) / len(cluster)
    validation['validation_criteria']['signal_quality'] = avg_score
    if avg_score >= 0.85:
        validation['green_flags'].append(f"High quality signals (avg {avg_score:.2f})")
    
    # Criteria 3: Location Confidence (weight: 15%)
    loc_confidence = location_data['primary_location']['confidence']
    validation['validation_criteria']['location_confidence'] = loc_confidence
    if loc_confidence >= 0.90:
        validation['green_flags'].append("High location confidence")
    elif loc_confidence < 0.70:
        validation['red_flags'].append("Low location confidence")
    
    # Criteria 4: Category Identification (weight: 10%)
    if business_idea['core_problem']['category']:
        validation['validation_criteria']['category_identified'] = 1.0
        validation['green_flags'].append("Category identified")
    else:
        validation['validation_criteria']['category_identified'] = 0.0
        validation['red_flags'].append("No clear category")
    
    # Criteria 5: Monetization Validation (weight: 15%)
    monetization_signals = sum(
        1 for s in cluster 
        if s.get('has_money_mention') or 'willing to pay' in s['text'].lower()
    )
    monetization_score = min(1.0, monetization_signals / len(cluster))
    validation['validation_criteria']['monetization'] = monetization_score
    if monetization_signals >= 2:
        validation['green_flags'].append(f"{monetization_signals} signals mention budget")
    
    # Criteria 6: Time Span (weight: 5%)
    dates = [s['scraped_at'] for s in cluster]
    time_span_days = (max(dates) - min(dates)).days
    if time_span_days <= 30:
        validation['validation_criteria']['time_span'] = 1.0
    elif time_span_days <= 60:
        validation['validation_criteria']['time_span'] = 0.7
    else:
        validation['validation_criteria']['time_span'] = 0.3
        validation['red_flags'].append(f"Signals spread over {time_span_days} days")
    
    # Criteria 7: Source Diversity (weight: 10%)
    sources = set(s['source'] for s in cluster)
    source_diversity = len(sources) / 3.0  # Normalize to 3 sources
    validation['validation_criteria']['source_diversity'] = min(1.0, source_diversity)
    if len(sources) >= 2:
        validation['green_flags'].append(f"Multiple sources: {', '.join(sources)}")
    
    # Calculate weighted validation score
    weights = {
        'signal_count': 0.20,
        'signal_quality': 0.25,
        'location_confidence': 0.15,
        'category_identified': 0.10,
        'monetization': 0.15,
        'time_span': 0.05,
        'source_diversity': 0.10
    }
    
    validation_score = sum(
        validation['validation_criteria'][k] * weights[k]
        for k in weights.keys()
    )
    
    validation['validation_score'] = round(validation_score, 2)
    
    # Determine confidence tier
    if validation_score >= 0.85:
        validation['confidence_tier'] = 'GOLDMINE'
        validation['passed'] = True
    elif validation_score >= 0.70:
        validation['confidence_tier'] = 'VALIDATED'
        validation['passed'] = True
    elif validation_score >= 0.50:
        validation['confidence_tier'] = 'WEAK_SIGNAL'
        validation['passed'] = False
    else:
        validation['confidence_tier'] = 'NOISE'
        validation['passed'] = False
    
    return validation
```

**Example Output:**

```python
validation_result = {
    'passed': True,
    'validation_score': 0.88,
    'confidence_tier': 'GOLDMINE',
    'validation_criteria': {
        'signal_count': 1.0,      # 8 signals
        'signal_quality': 0.87,   # Avg 0.87
        'location_confidence': 0.92,
        'category_identified': 1.0,
        'monetization': 0.75,     # 6/8 mention budget
        'time_span': 1.0,         # 23 days
        'source_diversity': 0.67  # 2 sources
    },
    'red_flags': [],
    'green_flags': [
        '8 signals (strong demand)',
        'High quality signals (avg 0.87)',
        'High location confidence',
        'Category identified',
        '6 signals mention budget',
        'Multiple sources: reddit, craigslist'
    ]
}
```

---

## 7. Deduplication & Merging

### Detect Duplicate Opportunities

```python
def find_duplicates(new_opportunity, existing_opportunities):
    """Find existing opportunities that might be duplicates"""
    
    duplicates = []
    
    for existing in existing_opportunities:
        similarity = calculate_opportunity_similarity(new_opportunity, existing)
        
        if similarity >= 0.75:
            duplicates.append({
                'opportunity': existing,
                'similarity': similarity
            })
    
    return duplicates

def calculate_opportunity_similarity(opp_a, opp_b):
    """Calculate similarity between two opportunities"""
    
    similarity = 0.0
    
    # Category match (40%)
    if opp_a['category'] == opp_b['category']:
        similarity += 0.40
    
    # Location match (30%)
    if opp_a['city'] == opp_b['city'] and opp_a['state'] == opp_b['state']:
        similarity += 0.30
    
    # Problem statement similarity (20%)
    problem_similarity = calculate_text_similarity(
        opp_a['problem_statement'],
        opp_b['problem_statement']
    )
    similarity += 0.20 * problem_similarity
    
    # Solution similarity (10%)
    solution_similarity = calculate_text_similarity(
        opp_a['solution_statement'],
        opp_b['solution_statement']
    )
    similarity += 0.10 * solution_similarity
    
    return similarity
```

### Merge Duplicate Opportunities

```python
def merge_opportunities(opportunity_a, opportunity_b):
    """Merge two duplicate opportunities"""
    
    merged = {
        # Keep higher confidence tier
        'confidence_tier': max_tier(
            opportunity_a['confidence_tier'],
            opportunity_b['confidence_tier']
        ),
        
        # Combine signal counts
        'signal_count': opportunity_a['signal_count'] + opportunity_b['signal_count'],
        
        # Average validation scores (weighted by signal count)
        'validation_score': weighted_average(
            opportunity_a['validation_score'], opportunity_a['signal_count'],
            opportunity_b['validation_score'], opportunity_b['signal_count']
        ),
        
        # Merge source lists
        'source_ids': list(set(
            opportunity_a['source_ids'] + opportunity_b['source_ids']
        )),
        
        # Use better problem statement (higher validation score)
        'problem_statement': (
            opportunity_a['problem_statement'] 
            if opportunity_a['validation_score'] >= opportunity_b['validation_score']
            else opportunity_b['problem_statement']
        ),
        
        # Merge key features
        'key_features': list(set(
            opportunity_a['key_features'] + opportunity_b['key_features']
        )),
        
        # Merge neighborhoods
        'neighborhoods': list(set(
            opportunity_a['neighborhoods'] + opportunity_b['neighborhoods']
        )),
        
        # Update timestamps
        'first_mentioned': min(
            opportunity_a['first_mentioned'],
            opportunity_b['first_mentioned']
        ),
        'last_mentioned': max(
            opportunity_a['last_mentioned'],
            opportunity_b['last_mentioned']
        )
    }
    
    return merged
```

---

## 8. Market Sizing

### Estimate Market Potential

```python
def estimate_market_size(opportunity, location_data):
    """Estimate total addressable market for opportunity"""
    
    market_size = {
        'potential_customers': None,
        'market_size_category': None,
        'revenue_potential': None,
        'competition_level': None
    }
    
    # Step 1: Estimate potential customers
    # Based on location population + problem category
    
    city_populations = {
        'San Francisco': 873965,
        'New York': 8336817,
        'Los Angeles': 3979576,
        'Chicago': 2693976,
        'Boston': 692600
    }
    
    base_population = city_populations.get(
        location_data['city'],
        500000  # Default estimate
    )
    
    # Apply coverage radius factor
    coverage_factor = min(1.0, location_data['coverage_radius'] / 15.0)
    reachable_population = int(base_population * coverage_factor)
    
    # Apply category penetration rate
    category_penetration = {
        'transportation': 0.40,  # 40% of people face this problem
        'childcare': 0.25,
        'home_services': 0.30,
        'healthcare': 0.35,
        'food_beverage': 0.50,
        'product_marketplace': 0.20,
        'service_marketplace': 0.25
    }
    
    penetration = category_penetration.get(opportunity['category'], 0.15)
    
    potential_customers = int(reachable_population * penetration)
    
    market_size['potential_customers'] = potential_customers
    
    # Step 2: Categorize market size
    if potential_customers >= 100000:
        market_size['market_size_category'] = 'LARGE'
    elif potential_customers >= 20000:
        market_size['market_size_category'] = 'MEDIUM'
    elif potential_customers >= 5000:
        market_size['market_size_category'] = 'SMALL'
    else:
        market_size['market_size_category'] = 'NICHE'
    
    # Step 3: Estimate revenue potential
    # Based on monetization signals and category
    
    avg_prices_mentioned = extract_price_points(opportunity['signals'])
    
    if avg_prices_mentioned:
        avg_price = sum(avg_prices_mentioned) / len(avg_prices_mentioned)
    else:
        # Default by category
        default_prices = {
            'transportation': 150,  # $150/month
            'childcare': 1500,      # $1500/month
            'home_services': 200,   # $200/service
            'product_marketplace': 50,  # $50/purchase
            'service_marketplace': 100  # $100/booking
        }
        avg_price = default_prices.get(opportunity['category'], 100)
    
    # Assume 5% market capture in year 1
    estimated_customers = potential_customers * 0.05
    
    # Annual revenue estimate
    annual_revenue = int(estimated_customers * avg_price * 12)
    
    market_size['revenue_potential'] = {
        'annual_revenue_estimate': annual_revenue,
        'avg_customer_value': avg_price,
        'estimated_customers_year1': int(estimated_customers)
    }
    
    # Step 4: Assess competition
    competition_keywords = [
        'already exists', 'similar to', 'like uber', 'competitor'
    ]
    
    competition_mentions = sum(
        1 for s in opportunity['signals']
        if any(kw in s['text'].lower() for kw in competition_keywords)
    )
    
    if competition_mentions >= 3:
        market_size['competition_level'] = 'HIGH'
    elif competition_mentions >= 1:
        market_size['competition_level'] = 'MEDIUM'
    else:
        market_size['competition_level'] = 'LOW'
    
    return market_size
```

**Example Output:**

```python
market_estimate = {
    'potential_customers': 87396,  # 10% of SF population in coverage area
    'market_size_category': 'MEDIUM',
    'revenue_potential': {
        'annual_revenue_estimate': 7865640,  # $7.8M
        'avg_customer_value': 150,  # $150/month
        'estimated_customers_year1': 4370  # 5% market capture
    },
    'competition_level': 'MEDIUM'
}
```

---

## 9. Output Format

### Final Opportunity Structure

```python
validated_opportunity = {
    # Identification
    'opportunity_id': 'OPP-20240115-SF-PARKING-001',
    'created_at': '2024-01-15T14:30:00Z',
    'updated_at': '2024-01-15T14:30:00Z',
    
    # Core Problem
    'problem': {
        'category': 'transportation',
        'subcategory': 'parking',
        'statement': 'San Francisco residents struggle to find affordable, convenient parking near transit stations and downtown',
        'keywords': ['parking', 'expensive', 'transit', 'downtown', 'available'],
    },
    
    # Solution
    'solution': {
        'type': 'software',
        'statement': 'Real-time parking availability app showing open spots near transit with monthly subscription',
        'key_features': [
            'Real-time spot availability',
            'Price comparison',
            'Near transit stations',
            'Monthly parking passes',
            'Reservations'
        ],
        'differentiation': [
            'Focus on transit-adjacent parking',
            'Flat monthly rate vs hourly',
            'Guaranteed spot availability'
        ]
    },
    
    # Location
    'location': {
        'city': 'San Francisco',
        'state': 'CA',
        'country': 'USA',
        'neighborhoods': ['Mission', 'SOMA', 'Downtown', 'Financial District'],
        'zip_codes': ['94103', '94110', '94105'],
        'latitude': 37.7749,
        'longitude': -122.4194,
        'coverage_radius_miles': 7.5,
        'density_type': 'city'
    },
    
    # Validation
    'validation': {
        'confidence_tier': 'GOLDMINE',
        'validation_score': 0.88,
        'signal_count': 8,
        'source_diversity': 2,
        'avg_signal_quality': 0.87,
        'location_confidence': 0.92,
        'monetization_validated': True,
        'green_flags': [
            '8 signals (strong demand)',
            'High quality signals',
            '6 signals mention budget'
        ],
        'red_flags': []
    },
    
    # Market Intelligence
    'market': {
        'potential_customers': 87396,
        'market_size_category': 'MEDIUM',
        'estimated_annual_revenue': 7865640,
        'avg_customer_value': 150,
        'competition_level': 'MEDIUM'
    },
    
    # Signal Traceability
    'signals': {
        'source_ids': ['reddit_abc123', 'craigslist_def456', ...],
        'sources': ['reddit', 'craigslist'],
        'first_mentioned': '2024-01-03T10:15:00Z',
        'last_mentioned': '2024-01-15T09:45:00Z',
        'time_span_days': 12
    },
    
    # Metadata
    'status': 'validated',
    'is_active': True,
    'reviewed': False,
    'assigned_to': None
}
```

---

## 10. Implementation Examples

### Complete Pipeline Function

```python
def process_raw_signals_to_opportunities(raw_signals):
    """
    Complete pipeline: raw signals → validated opportunities
    """
    
    # Stage 1: Filter low-quality signals
    high_quality_signals = [
        s for s in raw_signals 
        if s['signal_score'] >= 0.70
    ]
    
    print(f"Stage 1: {len(high_quality_signals)}/{len(raw_signals)} signals passed quality filter")
    
    # Stage 2: Cluster similar signals
    clusters = cluster_signals(high_quality_signals)
    
    print(f"Stage 2: Formed {len(clusters)} opportunity clusters")
    
    # Stage 3-8: Process each cluster
    validated_opportunities = []
    
    for i, cluster in enumerate(clusters):
        print(f"\nProcessing cluster {i+1}/{len(clusters)}...")
        
        # Stage 3: Extract business idea
        business_idea = extract_business_idea(cluster)
        
        # Stage 4: Validate location
        location_data = validate_cluster_location(cluster)
        
        # Stage 5: Calculate coverage
        coverage_area = calculate_coverage_area(cluster, location_data)
        
        # Stage 6: Validate opportunity
        validation = validate_opportunity(business_idea, cluster, location_data)
        
        if not validation['passed']:
            print(f"  ✗ Cluster failed validation (score: {validation['validation_score']})")
            continue
        
        print(f"  ✓ Cluster validated as {validation['confidence_tier']} (score: {validation['validation_score']})")
        
        # Stage 7: Check for duplicates
        duplicates = find_duplicates(business_idea, validated_opportunities)
        
        if duplicates:
            print(f"  → Merging with existing opportunity (similarity: {duplicates[0]['similarity']})")
            # Merge logic here
            continue
        
        # Stage 8: Market sizing
        market_estimate = estimate_market_size(business_idea, location_data)
        
        # Create final opportunity
        opportunity = create_opportunity_record(
            business_idea,
            location_data,
            coverage_area,
            validation,
            market_estimate,
            cluster
        )
        
        validated_opportunities.append(opportunity)
        
        print(f"  ✓ Created opportunity: {opportunity['opportunity_id']}")
    
    print(f"\n=== COMPLETE ===")
    print(f"Input: {len(raw_signals)} raw signals")
    print(f"Output: {len(validated_opportunities)} validated opportunities")
    print(f"Conversion rate: {len(validated_opportunities)/len(raw_signals)*100:.1f}%")
    
    return validated_opportunities
```

### Usage Example

```python
# Load raw scraped data
raw_signals = load_scraped_data_from_database()  # 100 signals

# Process through pipeline
opportunities = process_raw_signals_to_opportunities(raw_signals)

# Results:
# Input: 100 raw signals
# Stage 1: 73/100 signals passed quality filter
# Stage 2: Formed 18 opportunity clusters
#
# Processing cluster 1/18...
#   ✓ Cluster validated as GOLDMINE (score: 0.88)
#   ✓ Created opportunity: OPP-20240115-SF-PARKING-001
#
# [...]
#
# === COMPLETE ===
# Input: 100 raw signals  
# Output: 12 validated opportunities
# Conversion rate: 12.0%

# Save to database
for opportunity in opportunities:
    save_opportunity_to_database(opportunity)

print(f"\nSaved {len(opportunities)} opportunities to database")
```

---

## Summary

This algorithm transforms **100 raw signals** into **~12 validated opportunities** through:

1. ✅ **Pattern matching** (0.70+ threshold)
2. ✅ **Clustering** (group similar problems)
3. ✅ **Business idea extraction** (what to build)
4. ✅ **Location validation** (where demand is)
5. ✅ **Opportunity validation** (confidence scoring)
6. ✅ **Deduplication** (merge duplicates)
7. ✅ **Market sizing** (estimate potential)
8. ✅ **Structured output** (ready for database)

**Output: Validated, location-mapped business opportunities ready for action!**
