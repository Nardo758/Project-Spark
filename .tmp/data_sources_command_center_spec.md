# **Admin Panel Technical Design Document**

## **System Architecture**

### **1. High-Level Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scrapers      │────│   API Gateway   │────│   Core Engine   │
│  (External)     │    │  (Rate Limiting │    │  (Validation    │
└─────────────────┘    │   & Auth)       │    │   Pipeline)     │
                       └─────────────────┘    └─────────┬───────┘
                                                            │
┌─────────────────┐    ┌─────────────────┐    ┌───────────▼───────┐
│   Admin Panel   │────│   WebSocket     │────│   Real-time       │
│  (React/Vue)    │    │   Server        │    │   Processing      │
└─────────────────┘    └─────────────────┘    └─────────┬───────┘
                                                            │
┌─────────────────┐    ┌─────────────────┐    ┌───────────▼───────┐
│   External      │────│   Cache Layer   │────│   Data Stores     │
│   Services      │    │  (Redis)        │    │  (PostgreSQL,     │
└─────────────────┘    └─────────────────┘    │   Elasticsearch)  │
                                              └───────────────────┘
```

### **2. Database Schema Design**

#### **Core Tables**

```sql
-- Raw scraped data (before validation)
CREATE TABLE raw_scrapes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL, -- 'reddit', 'craigslist', 'yelp', etc.
    source_id VARCHAR(255) UNIQUE, -- Original ID from source
    content TEXT NOT NULL,
    metadata JSONB NOT NULL, -- Includes source-specific fields
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);

-- Processed opportunities
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_scrape_id UUID REFERENCES raw_scrapes(id),
    title VARCHAR(500),
    content TEXT NOT NULL,
    
    -- Location data
    location_city VARCHAR(100),
    location_state VARCHAR(50),
    location_neighborhood VARCHAR(100),
    location_confidence DECIMAL(3,2) CHECK (location_confidence >= 0 AND location_confidence <= 1),
    location_raw TEXT, -- Original location text
    location_source VARCHAR(50), -- How location was extracted
    
    -- Business idea extraction
    business_description TEXT,
    category VARCHAR(100),
    subcategories TEXT[], -- Multiple categories if applicable
    
    -- Pattern matches
    matched_patterns JSONB[], -- Array of pattern objects that matched
    pattern_scores JSONB, -- Scores per pattern type
    
    -- Quantifications
    money_mentions JSONB, -- {amount: 20, currency: 'USD', period: 'month'}
    time_mentions JSONB, -- {value: 2, unit: 'hours'}
    frequency_mentions JSONB,
    
    -- Scoring
    base_score DECIMAL(3,2),
    location_boost DECIMAL(3,2),
    quantification_boost DECIMAL(3,2),
    multi_signal_boost DECIMAL(3,2),
    engagement_boost DECIMAL(3,2),
    source_weight DECIMAL(3,2),
    final_score DECIMAL(3,2) CHECK (final_score >= 0 AND final_score <= 1),
    
    -- Tier classification
    tier VARCHAR(20) CHECK (tier IN ('GOLDMINE', 'VALIDATED', 'WEAK_SIGNAL', 'NOISE')),
    recommended_action VARCHAR(50),
    
    -- Status
    status VARCHAR(20) DEFAULT 'NEW' CHECK (status IN ('NEW', 'REVIEWED', 'ACTIONED', 'ARCHIVED')),
    assigned_to UUID REFERENCES users(id),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    
    -- Indexes
    INDEX idx_opportunities_score (final_score DESC),
    INDEX idx_opportunities_tier (tier),
    INDEX idx_opportunities_location (location_city, location_state),
    INDEX idx_opportunities_category (category),
    INDEX idx_opportunities_created (created_at DESC)
);

-- Pattern management
CREATE TABLE patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    regex_pattern TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    source_specific JSONB, -- Which sources this applies to
    validation_level VARCHAR(20), -- goldmine, validated, etc.
    
    -- Effectiveness tracking
    hit_count INTEGER DEFAULT 0,
    false_positive_count INTEGER DEFAULT 0,
    last_matched_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_patterns_category (category),
    INDEX idx_patterns_confidence (confidence DESC)
);

-- Category definitions
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    keywords TEXT[] NOT NULL,
    opportunity_types TEXT[],
    weight DECIMAL(3,2) DEFAULT 1.0,
    
    -- Performance metrics
    match_count INTEGER DEFAULT 0,
    average_score DECIMAL(3,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Source configuration
CREATE TABLE sources (
    name VARCHAR(50) PRIMARY KEY,
    base_weight DECIMAL(3,2) DEFAULT 1.0,
    location_extraction_config JSONB,
    rate_limit_per_minute INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Performance tracking
    total_scrapes INTEGER DEFAULT 0,
    valid_opportunities INTEGER DEFAULT 0,
    average_score DECIMAL(3,2),
    
    last_scraped_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Review and actions
CREATE TABLE opportunity_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID REFERENCES opportunities(id),
    user_id UUID REFERENCES users(id),
    
    action VARCHAR(50), -- 'approved', 'rejected', 'needs_more_info'
    notes TEXT,
    confidence_adjustment DECIMAL(3,2), -- Manual score adjustment
    tags TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_reviews_opportunity (opportunity_id)
);

-- System metrics and audit
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(50), -- 'processing_rate', 'false_positive_rate', etc.
    value DECIMAL(10,2),
    metadata JSONB,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_metrics_type_time (metric_type, recorded_at DESC)
);
```

#### **Geospatial Support**
```sql
-- Enable PostGIS for geographic queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- Add geography column to opportunities
ALTER TABLE opportunities ADD COLUMN location_geography GEOGRAPHY(Point);

-- Create spatial index
CREATE INDEX idx_opportunities_geography ON opportunities USING GIST(location_geography);
```

#### **Full-Text Search Optimization**
```sql
-- Add full-text search vector
ALTER TABLE opportunities 
ADD COLUMN search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(content, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(business_description, '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(category, '')), 'D')
) STORED;

-- Create GIN index for fast text search
CREATE INDEX idx_opportunities_search ON opportunities USING GIN(search_vector);
```

### **3. API Design**

#### **REST API Endpoints**

```python
# FastAPI/Sanic/Tornado structure
# app/api/v1/

# ===== Core Processing =====
@router.post("/process")
async def process_scraped_data(
    items: List[ScrapeItem],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Process scraped data through validation pipeline
    """
    pass

@router.get("/opportunities/{opportunity_id}")
async def get_opportunity_details(
    opportunity_id: UUID,
    include_raw: bool = False,
    current_user: User = Depends(get_current_user)
) -> OpportunityDetailResponse:
    """
    Get full details of an opportunity including scoring breakdown
    """
    pass

# ===== Pattern Management =====
@router.get("/patterns")
async def list_patterns(
    category: Optional[str] = None,
    active_only: bool = True,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
) -> PatternListResponse:
    pass

@router.post("/patterns")
async def create_pattern(
    pattern: PatternCreate,
    current_user: User = Depends(get_current_user)
) -> PatternResponse:
    pass

@router.put("/patterns/{pattern_id}")
async def update_pattern(
    pattern_id: UUID,
    pattern: PatternUpdate,
    current_user: User = Depends(get_current_user)
) -> PatternResponse:
    pass

# ===== Dashboard Data =====
@router.get("/dashboard/summary")
async def get_dashboard_summary(
    time_range: str = "7d",  # 24h, 7d, 30d, 90d
    current_user: User = Depends(get_current_user)
) -> DashboardSummary:
    """
    High-level summary for dashboard
    """
    pass

@router.get("/dashboard/geographic")
async def get_geographic_data(
    category_filter: Optional[str] = None,
    score_min: float = 0.7,
    current_user: User = Depends(get_current_user)
) -> GeographicDataResponse:
    """
    Get data for geographic heatmap
    """
    pass

@router.get("/dashboard/tier-distribution")
async def get_tier_distribution(
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> TierDistributionResponse:
    pass

# ===== Review Workflow =====
@router.post("/opportunities/{opportunity_id}/review")
async def review_opportunity(
    opportunity_id: UUID,
    review: ReviewCreate,
    current_user: User = Depends(get_current_user)
) -> ReviewResponse:
    """
    Submit a review for an opportunity
    """
    pass

@router.get("/review-queue")
async def get_review_queue(
    tier: Optional[str] = "GOLDMINE",
    assigned_to_me: bool = False,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
) -> ReviewQueueResponse:
    pass

# ===== Batch Operations =====
@router.post("/opportunities/batch-action")
async def batch_action(
    action: BatchAction,
    current_user: User = Depends(get_current_user)
) -> BatchActionResponse:
    """
    Perform batch actions on opportunities
    """
    pass

@router.post("/export")
async def export_opportunities(
    filters: ExportFilters,
    format: str = "csv",  # csv, json, excel
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    Export filtered opportunities
    """
    pass
```

#### **WebSocket/SSE Endpoints**
```python
# Real-time updates
@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send real-time updates
            data = await get_realtime_metrics()
            await websocket.send_json(data)
            await asyncio.sleep(5)  # Update every 5 seconds
    except WebSocketDisconnect:
        pass

@router.get("/sse/opportunities")
async def opportunity_stream(
    tier: str = "GOLDMINE",
    current_user: User = Depends(get_current_user)
):
    """
    Server-Sent Events for new opportunities
    """
    async def event_generator():
        last_id = None
        while True:
            # Query for new opportunities since last_id
            new_opps = await get_new_opportunities_since(last_id, tier)
            for opp in new_opps:
                yield {
                    "event": "new_opportunity",
                    "data": opp.dict()
                }
                last_id = opp.id
            await asyncio.sleep(1)
    
    return EventSourceResponse(event_generator())
```

### **4. Processing Pipeline Architecture**

```python
# app/core/pipeline.py

class ValidationPipeline:
    """Multi-stage validation pipeline"""
    
    def __init__(self):
        self.stages = [
            self._preprocess,
            self._extract_location,
            self._match_patterns,
            self._classify_category,
            self._extract_quantifications,
            self._calculate_score,
            self._assign_tier
        ]
    
    async def process(self, scraped_data: ScrapedItem) -> Opportunity:
        """Process scraped data through all stages"""
        context = {
            'raw': scraped_data,
            'results': {},
            'errors': []
        }
        
        for stage in self.stages:
            try:
                await stage(context)
            except Exception as e:
                context['errors'].append({
                    'stage': stage.__name__,
                    'error': str(e)
                })
                # Continue with next stage or handle based on error severity
        
        return self._create_opportunity(context)
    
    async def _extract_location(self, context: dict):
        """Stage 1: Location extraction"""
        source_strategy = SOURCE_LOCATION_STRATEGIES.get(context['raw'].source)
        
        if not source_strategy:
            # Fallback to text analysis
            location_data = await self._analyze_text_for_location(context['raw'].content)
        else:
            location_data = await self._apply_source_strategy(
                context['raw'], 
                source_strategy
            )
        
        context['results']['location'] = location_data
    
    async def _match_patterns(self, context: dict):
        """Stage 2: Pattern matching using keyword matrix"""
        matches = []
        
        for category, patterns in BUSINESS_IDEA_KEYWORDS.items():
            for pattern_config in patterns:
                if self._pattern_matches(pattern_config, context['raw'].content):
                    matches.append({
                        'category': category,
                        'pattern': pattern_config['name'],
                        'confidence': pattern_config['confidence'],
                        'matched_text': self._extract_match(pattern_config, context['raw'].content)
                    })
        
        # Sort by confidence and deduplicate
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        context['results']['pattern_matches'] = matches
    
    async def _calculate_score(self, context: dict):
        """Stage 6: Composite scoring"""
        scores = calculate_composite_score(context['results'])
        context['results']['scores'] = scores
```

### **5. Caching Strategy**

```python
# app/core/cache.py

import redis
from functools import wraps
from typing import Optional, Callable

class CacheManager:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        
    def cache(
        self,
        key_prefix: str,
        ttl: int = 300,  # 5 minutes default
        version: int = 1
    ):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from arguments
                cache_key = f"{key_prefix}:{version}:{self._make_key(args, kwargs)}"
                
                # Try to get from cache
                cached = await self.get(cache_key)
                if cached is not None:
                    return cached
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    async def invalidate_patterns(self):
        """Invalidate all pattern-related caches"""
        keys = self.redis.keys("patterns:*")
        if keys:
            self.redis.delete(*keys)

# Usage example
cache = CacheManager()

@cache.cache("dashboard_summary", ttl=60)
async def get_dashboard_summary(time_range: str) -> dict:
    """This will be cached for 60 seconds"""
    # Expensive database queries
    pass
```

### **6. Real-time Processing with Celery/RQ**

```python
# app/tasks.py

from celery import Celery
from app.core.pipeline import ValidationPipeline

app = Celery('oppgrid')
app.config_from_object('celeryconfig')

@app.task
def process_scraped_batch(batch_data: List[dict]):
    """Process a batch of scraped data"""
    pipeline = ValidationPipeline()
    results = []
    
    for item in batch_data:
        try:
            opportunity = pipeline.process(item)
            results.append(opportunity)
            
            # Send real-time update via WebSocket
            send_websocket_update({
                'type': 'opportunity_processed',
                'data': opportunity.to_dict()
            })
        except Exception as e:
            log_error(f"Failed to process item {item.get('id')}: {str(e)}")
    
    return results

@app.task
def recalculate_scores(pattern_id: Optional[str] = None):
    """Recalculate scores for opportunities (e.g., after pattern update)"""
    query = Opportunity.objects.all()
    
    if pattern_id:
        # Only recalculate opportunities with this pattern
        query = query.filter(matched_patterns__contains=[pattern_id])
    
    for opportunity in query:
        new_score = calculate_composite_score(opportunity)
        opportunity.update_score(new_score)
        opportunity.save()
```

### **7. Frontend Architecture (React)**

```typescript
// src/components/
├── Dashboard/
│   ├── Dashboard.tsx
│   ├── SummaryCards.tsx
│   ├── GeographicHeatmap.tsx
│   └── TierDistribution.tsx
├── Opportunities/
│   ├── OpportunityList.tsx
│   ├── OpportunityCard.tsx
│   ├── OpportunityDetail.tsx
│   └── ReviewQueue.tsx
├── Patterns/
│   ├── PatternManager.tsx
│   ├── PatternEditor.tsx
│   └── PatternPerformance.tsx
├── Sources/
│   ├── SourceManager.tsx
│   └── SourceMetrics.tsx
└── Analytics/
    ├── AnalyticsDashboard.tsx
    └── CategoryAnalytics.tsx

// src/services/api.ts
export interface Opportunity {
  id: string;
  content: string;
  location: LocationData;
  category: string;
  tier: 'GOLDMINE' | 'VALIDATED' | 'WEAK_SIGNAL' | 'NOISE';
  final_score: number;
  score_breakdown: ScoreBreakdown;
  created_at: string;
}

export interface ScoreBreakdown {
  base_score: number;
  location_boost: number;
  quantification_boosts: number;
  multi_signal_boost: number;
  engagement_boost: number;
}

// Real-time WebSocket service
class WebSocketService {
  private socket: WebSocket | null = null;
  private listeners: Map<string, Function[]> = new Map();
  
  connect() {
    this.socket = new WebSocket(`${API_URL}/ws/dashboard`);
    
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.emit(data.event, data.data);
    };
  }
  
  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }
  
  emit(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }
}
```

### **8. Monitoring & Observability**

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    
  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    
  redis-exporter:
    image: oliver006/redis_exporter
    environment:
      - REDIS_ADDR=redis:6379
    
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      - DATA_SOURCE_NAME=postgresql://user:pass@postgres:5432/oppgrid?sslmode=disable
```

```python
# app/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Define metrics
OPPORTUNITIES_PROCESSED = Counter(
    'opportunities_processed_total',
    'Total number of opportunities processed',
    ['source', 'tier']
)

PROCESSING_DURATION = Histogram(
    'opportunity_processing_duration_seconds',
    'Time spent processing an opportunity',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

PATTERN_MATCHES = Counter(
    'pattern_matches_total',
    'Total pattern matches',
    ['pattern_name', 'category']
)

SCORE_DISTRIBUTION = Histogram(
    'opportunity_score_distribution',
    'Distribution of opportunity scores',
    buckets=(0.1, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0)
)

# Usage in pipeline
@PROCESSING_DURATION.time()
async def process_opportunity(item):
    result = await pipeline.process(item)
    
    # Increment counters
    OPPORTUNITIES_PROCESSED.labels(
        source=item.source,
        tier=result.tier
    ).inc()
    
    PATTERN_MATCHES.labels(
        pattern_name=result.primary_pattern,
        category=result.category
    ).inc()
    
    SCORE_DISTRIBUTION.observe(result.final_score)
    
    return result
```

### **9. Security & Rate Limiting**

```python
# app/security/rate_limit.py

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Different rate limits for different endpoints
@router.post("/api/process")
@limiter.limit("100/minute")
async def process_data():
    pass

@router.get("/api/dashboard")
@limiter.limit("30/minute")
async def get_dashboard():
    pass

# API Key authentication
def validate_api_key(api_key: str) -> bool:
    """Validate scraper API key"""
    return api_key in settings.VALID_API_KEYS

# JWT for admin panel
@app.post("/api/auth/login")
async def login(username: str, password: str):
    user = authenticate(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

### **10. Deployment Configuration**

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: oppgrid
      POSTGRES_USER: oppgrid
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
  
  api:
    build: .
    image: oppgrid-api:latest
    environment:
      DATABASE_URL: postgresql://oppgrid:${DB_PASSWORD}@postgres/oppgrid
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
  
  celery-worker:
    build: .
    image: oppgrid-api:latest
    command: celery -A app.tasks worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://oppgrid:${DB_PASSWORD}@postgres/oppgrid
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - redis
      - api
  
  celery-beat:
    build: .
    image: oppgrid-api:latest
    command: celery -A app.tasks beat --loglevel=info
    environment:
      DATABASE_URL: postgresql://oppgrid:${DB_PASSWORD}@postgres/oppgrid
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - redis
      - api
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

### **11. Testing Strategy**

```python
# tests/test_pipeline.py

import pytest
from app.core.pipeline import ValidationPipeline

@pytest.fixture
def pipeline():
    return ValidationPipeline()

@pytest.mark.asyncio
async def test_location_extraction_high_confidence(pipeline):
    """Test extraction of high-confidence locations"""
    scraped_item = {
        'source': 'reddit',
        'content': 'I need parking in San Francisco, CA',
        'metadata': {'subreddit': 'sanfrancisco'}
    }
    
    result = await pipeline.process(scraped_item)
    
    assert result.location_city == 'San Francisco'
    assert result.location_state == 'CA'
    assert result.location_confidence >= 0.9

@pytest.mark.parametrize("input_text,expected_tier", [
    ("I wish there was an app for parking", "GOLDMINE"),
    ("Parking is frustrating", "VALIDATED"),
    ("parking here", "WEAK_SIGNAL"),
])
async def test_tier_classification(pipeline, input_text, expected_tier):
    """Test tier classification for different input texts"""
    scraped_item = {
        'source': 'reddit',
        'content': input_text,
        'metadata': {'subreddit': 'sanfrancisco'}
    }
    
    result = await pipeline.process(scraped_item)
    assert result.tier == expected_tier

# Load testing
@pytest.mark.benchmark
async def test_pipeline_performance(benchmark):
    """Benchmark pipeline performance"""
    pipeline = ValidationPipeline()
    sample_data = generate_sample_data(1000)
    
    result = benchmark(pipeline.process_batch, sample_data)
    assert result['processing_time'] < 10  # Should process 1000 items in <10 seconds
```

This technical design provides a robust, scalable architecture for your admin panel that can handle the complex validation pipeline while providing real-time insights and management capabilities.