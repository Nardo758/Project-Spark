# AI Router Integration Guide

## Overview
The AI Router automatically routes tasks to the most cost-effective model based on task complexity.

## Quick Start

### Basic Usage
```python
from app.services.ai_router import AIRouter, TaskType

# Initialize router
router = AIRouter()

# Route a task
result = router.route(
    task_type=TaskType.CODE_GENERATION,
    prompt="Write a Python function to calculate factorial"
)

print(result["response"])  # The generated code
print(f"Cost: ${result['estimated_cost_usd']}")  # $0.003
print(f"Model used: {result['model_used']}")  # openai_gpt4
```

### Convenience Functions
```python
from app.services.ai_router import (
    analyze_opportunity,
    generate_code,
    search_and_summarize,
    classify_opportunity_category
)

# Analyze opportunity (uses Sonnet)
analysis = analyze_opportunity("Freelance invoicing is a nightmare...")

# Generate code (uses GPT-4 - cheaper)
code = generate_code("Create a React component for opportunity cards")

# Web search (uses Gemini - cheapest)
summary = search_and_summarize("Latest trends in freelance tools")

# Simple classification (uses Haiku - fastest)
category = classify_opportunity_category(
    "Parking in cities",
    "Takes 30 minutes to find a spot..."
)
```

## Integration Points

### 1. Update AI Co-Founder Service
**File:** `app/services/ai_cofounder.py`

```python
# OLD (everything uses Sonnet)
from anthropic import Anthropic
client = Anthropic(...)
response = client.messages.create(...)

# NEW (smart routing)
from app.services.ai_router import AIRouter, TaskType

router = AIRouter(user_api_key=user.api_key if user.byok_enabled else None)

# For conversation (brain task - uses Sonnet)
result = router.route(
    task_type=TaskType.USER_CONVERSATION,
    prompt=user_message,
    system_prompt=STAGE_PROMPTS[stage]
)

# For code suggestions (muscle task - uses GPT-4)
code_result = router.route(
    task_type=TaskType.CODE_GENERATION,
    prompt=f"Generate {language} code for: {task_description}"
)
```

### 2. Update Opportunity Analysis
**File:** `app/routers/ai_analysis.py`

```python
from app.services.ai_router import analyze_opportunity

@router.post("/analyze/{opportunity_id}")
async def analyze_opportunity_endpoint(
    opportunity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    
    # Uses Sonnet (complex analysis)
    analysis = analyze_opportunity(
        f"{opportunity.title}\n\n{opportunity.description}",
        user_api_key=current_user.anthropic_api_key if current_user.byok_enabled else None
    )
    
    return {"analysis": analysis}
```

### 3. Update Scrapers (Classification)
**File:** `app/routers/scraper.py`

```python
from app.services.ai_router import classify_opportunity_category

def process_scraped_post(post):
    # OLD: Expensive Sonnet call for simple classification
    # NEW: Fast + cheap Haiku classification
    category = classify_opportunity_category(
        post['title'],
        post['description']
    )
    
    opportunity = Opportunity(
        title=post['title'],
        description=post['description'],
        category=category,  # Classified with Haiku ($0.0001 vs $0.003)
        ...
    )
```

### 4. Update Research Tools
**File:** `app/services/consultant_studio.py`

```python
from app.services.ai_router import AIRouter, TaskType

def generate_market_insights(location_data, competitor_data):
    router = AIRouter()
    
    # Data summarization (uses Gemini - cheap)
    summary = router.route(
        task_type=TaskType.DATA_SUMMARIZATION,
        prompt=f"Summarize this market data:\n\nLocations: {location_data}\nCompetitors: {competitor_data}"
    )
    
    return summary["response"]
```

## Task Type Reference

| Task Type | Model Used | Cost (per 1M tokens) | Use Case |
|-----------|------------|---------------------|----------|
| `COMPLEX_REASONING` | Sonnet | $3-15 | Strategic decisions |
| `STRATEGIC_ANALYSIS` | Sonnet | $3-15 | Opportunity analysis |
| `USER_CONVERSATION` | Sonnet | $3-15 | AI co-founder chat |
| `OPPORTUNITY_ANALYSIS` | Sonnet | $3-15 | Feasibility scoring |
| `CODE_GENERATION` | GPT-4 | $10-30 | Write code |
| `CODE_DEBUG` | GPT-4 | $10-30 | Fix bugs |
| `WEB_SEARCH` | Gemini | $0.5-1.5 | Search & summarize |
| `DATA_SUMMARIZATION` | Gemini | $0.5-1.5 | Condense data |
| `SOCIAL_ANALYSIS` | Gemini | $0.5-1.5 | Analyze social posts |
| `TREND_DETECTION` | Gemini | $0.5-1.5 | Identify patterns |
| `SIMPLE_CLASSIFICATION` | Haiku | $0.25-1.25 | Categorize opportunities |

## Cost Tracking

```python
# Track costs per session
router = AIRouter()

# Make multiple calls
router.route(TaskType.CODE_GENERATION, "...")
router.route(TaskType.WEB_SEARCH, "...")
router.route(TaskType.OPPORTUNITY_ANALYSIS, "...")

# Get summary
summary = router.get_usage_summary()
print(f"Total cost: ${summary['total_cost_usd']}")
print(f"Total tokens: {summary['total_tokens']}")
print(f"Models used: {summary['models_used']}")

# Output:
# Total cost: $0.0456
# Total tokens: {'input': 1240, 'output': 890}
# Models used: {'openai_gpt4': 1, 'google_gemini': 1, 'anthropic_sonnet': 1}
```

## Best Practices

### 1. Choose the Right Task Type
```python
# ❌ Wrong - uses expensive Sonnet for simple task
router.route(
    task_type=TaskType.COMPLEX_REASONING,
    prompt="Classify this as Tech or Finance"
)

# ✅ Right - uses cheap Haiku
router.route(
    task_type=TaskType.SIMPLE_CLASSIFICATION,
    prompt="Classify this as Tech or Finance"
)
```

### 2. Batch Similar Tasks
```python
# ❌ Wrong - 100 separate expensive calls
for opportunity in opportunities:
    analyze_opportunity(opportunity.description)

# ✅ Right - 1 cheaper summarization call
all_opps = "\n\n".join([f"{o.title}: {o.description}" for o in opportunities])
router.route(
    task_type=TaskType.DATA_SUMMARIZATION,
    prompt=f"Summarize these opportunities:\n{all_opps}"
)
```

### 3. Use BYOK When Available
```python
# If user provides their own API key, use it (no cost to us)
router = AIRouter(user_api_key=current_user.anthropic_api_key)
```

## Migration Checklist

- [ ] Replace anthropic client calls with router in `ai_cofounder.py`
- [ ] Update `ai_analysis.py` to use `analyze_opportunity()`
- [ ] Update scrapers to use `classify_opportunity_category()`
- [ ] Update research services to use `search_and_summarize()`
- [ ] Add cost tracking to admin dashboard
- [ ] Monitor cost savings (target: 40-60% reduction)
- [ ] A/B test quality (ensure cheaper models perform well)

## Expected Cost Reduction

**Before Router:**
- Average cost per API call: $0.03
- Daily API calls: 10,000
- Monthly cost: $9,000

**After Router:**
- Average cost per API call: $0.012 (60% reduction)
- Daily API calls: 10,000
- Monthly cost: $3,600

**Savings: $5,400/month**

## Monitoring

Add to admin dashboard:
```python
@router.get("/admin/ai-costs")
def get_ai_costs(db: Session = Depends(get_db)):
    # Query usage logs
    daily_costs = db.query(
        func.date(AIUsageLog.created_at).label('date'),
        func.sum(AIUsageLog.cost_usd).label('total_cost'),
        func.count(AIUsageLog.id).label('call_count')
    ).group_by('date').order_by(desc('date')).limit(30).all()
    
    return {
        "daily_costs": [
            {"date": str(d.date), "cost": float(d.total_cost), "calls": d.call_count}
            for d in daily_costs
        ]
    }
```

## Troubleshooting

### API Keys Missing
```python
# Set environment variables
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AI..."
export AI_INTEGRATIONS_ANTHROPIC_API_KEY="sk-ant-..."
```

### Model Not Available
```python
# Fallback to Sonnet if specialized model fails
try:
    result = router.route(TaskType.CODE_GENERATION, prompt)
except Exception as e:
    result = router.route(
        TaskType.COMPLEX_REASONING,
        prompt,
        force_model=ModelProvider.ANTHROPIC_SONNET
    )
```

### Quality Issues
```python
# If cheaper model produces poor results, override routing
result = router.route(
    task_type=TaskType.DATA_SUMMARIZATION,
    prompt=prompt,
    force_model=ModelProvider.ANTHROPIC_SONNET  # Force high-quality model
)
```
