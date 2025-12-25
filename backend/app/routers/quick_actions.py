"""
Quick Actions API Router
Business Plan Generator, Financial Models, Pitch Deck Assistant
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import json
import time
import logging

from app.db.database import get_db
from app.services.llm_ai_engine import get_anthropic_client

router = APIRouter(prefix="/quick-actions", tags=["Quick Actions"])
logger = logging.getLogger(__name__)


class BusinessPlanRequest(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=200)
    business_description: str = Field(..., min_length=10, max_length=5000)
    industry: str = Field(..., min_length=2, max_length=100)
    target_market: str = Field(..., min_length=2, max_length=100)


class BusinessPlanResponse(BaseModel):
    success: bool
    plan: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class FinancialsRequest(BaseModel):
    projection_period: str = Field(default="3 Years")
    business_model: str = Field(default="Subscription (SaaS)")
    starting_capital: Optional[float] = None
    expected_monthly_revenue: Optional[float] = None
    business_description: Optional[str] = None


class FinancialsResponse(BaseModel):
    success: bool
    financials: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class PitchDeckRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    one_line_pitch: str = Field(..., min_length=10, max_length=500)
    funding_stage: str = Field(default="Seed")
    amount_raising: Optional[float] = None
    business_description: Optional[str] = None


class PitchDeckResponse(BaseModel):
    success: bool
    pitch_deck: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """Parse AI response, handling markdown code blocks."""
    text = response_text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_response": text}


@router.post("/business-plan", response_model=BusinessPlanResponse)
async def generate_business_plan(request: BusinessPlanRequest, db: Session = Depends(get_db)):
    """Generate a comprehensive business plan using AI."""
    start_time = time.time()
    
    client = get_anthropic_client()
    if not client:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        prompt = f"""Generate a comprehensive business plan for this business:

BUSINESS DETAILS:
- Name: {request.business_name}
- Description: {request.business_description}
- Industry: {request.industry}
- Target Market: {request.target_market}

Create a detailed JSON business plan with these sections:
1. "executive_summary": {{
   "vision": "company vision statement",
   "mission": "mission statement",
   "value_proposition": "unique value proposition",
   "business_model": "how the business makes money"
}}
2. "market_analysis": {{
   "market_size": "total addressable market estimate",
   "target_demographics": "ideal customer profile",
   "market_trends": ["trend1", "trend2", "trend3"],
   "competitive_landscape": "brief competitive analysis"
}}
3. "products_services": {{
   "core_offerings": ["offering1", "offering2"],
   "pricing_strategy": "pricing approach",
   "differentiation": "what makes this unique"
}}
4. "marketing_strategy": {{
   "channels": ["channel1", "channel2", "channel3"],
   "customer_acquisition": "how to acquire customers",
   "brand_positioning": "market positioning"
}}
5. "operations_plan": {{
   "key_activities": ["activity1", "activity2"],
   "resources_needed": ["resource1", "resource2"],
   "partnerships": "potential strategic partnerships"
}}
6. "financial_projections": {{
   "startup_costs": "estimated startup costs",
   "revenue_year_1": "year 1 revenue estimate",
   "revenue_year_3": "year 3 revenue estimate",
   "break_even": "estimated break-even timeline"
}}
7. "team_management": {{
   "key_roles": ["role1", "role2", "role3"],
   "hiring_plan": "first year hiring priorities",
   "advisors_needed": "advisory board recommendations"
}}
8. "funding_requirements": {{
   "amount_needed": "initial funding requirement",
   "use_of_funds": ["use1", "use2", "use3"],
   "milestones": ["milestone1", "milestone2"]
}}

Respond only with valid JSON."""

        response = client.messages.create(
            model="claude-haiku-4-5-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = parse_ai_response(response.content[0].text)
        processing_time = int((time.time() - start_time) * 1000)
        
        return BusinessPlanResponse(
            success=True,
            plan=result,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Business plan generation failed: {e}")
        return BusinessPlanResponse(
            success=False,
            error=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )


@router.post("/financials", response_model=FinancialsResponse)
async def generate_financial_model(request: FinancialsRequest, db: Session = Depends(get_db)):
    """Generate financial projections and models using AI."""
    start_time = time.time()
    
    client = get_anthropic_client()
    if not client:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        prompt = f"""Generate detailed financial projections and models:

PARAMETERS:
- Projection Period: {request.projection_period}
- Business Model: {request.business_model}
- Starting Capital: ${request.starting_capital or 50000:,.0f}
- Expected Monthly Revenue (Year 1): ${request.expected_monthly_revenue or 10000:,.0f}
- Business Description: {request.business_description or 'Not provided'}

Create a comprehensive JSON financial model with:
1. "revenue_projections": {{
   "year_1": {{"monthly": [12 monthly values], "total": total}},
   "year_2": {{"quarterly": [4 quarterly values], "total": total}},
   "year_3": {{"quarterly": [4 quarterly values], "total": total}},
   "growth_assumptions": "growth rate assumptions"
}}
2. "cost_structure": {{
   "fixed_costs": {{"items": [{{"name": "cost name", "monthly": amount}}], "total_monthly": total}},
   "variable_costs": {{"items": [{{"name": "cost name", "percentage": pct}}], "cogs_percentage": pct}},
   "operating_expenses": {{"monthly": amount, "annual": amount}}
}}
3. "break_even_analysis": {{
   "break_even_revenue": "monthly revenue needed",
   "break_even_units": "units if applicable",
   "months_to_break_even": number,
   "assumptions": ["assumption1", "assumption2"]
}}
4. "cash_flow": {{
   "initial_cash": starting capital,
   "monthly_burn_rate": amount,
   "runway_months": number,
   "cash_flow_positive_month": number
}}
5. "profit_loss_forecast": {{
   "year_1": {{"revenue": amount, "costs": amount, "net_income": amount, "margin": pct}},
   "year_2": {{"revenue": amount, "costs": amount, "net_income": amount, "margin": pct}},
   "year_3": {{"revenue": amount, "costs": amount, "net_income": amount, "margin": pct}}
}}
6. "unit_economics": {{
   "customer_acquisition_cost": amount,
   "lifetime_value": amount,
   "ltv_cac_ratio": ratio,
   "payback_period_months": number
}}
7. "funding_runway": {{
   "current_runway": "months at current burn",
   "recommended_raise": amount,
   "post_raise_runway": "months after raising"
}}
8. "key_metrics": {{
   "mrr_year_1_end": amount,
   "arr_year_1_end": amount,
   "gross_margin": percentage,
   "net_margin_year_3": percentage
}}

Use realistic numbers based on the business model. Respond only with valid JSON."""

        response = client.messages.create(
            model="claude-haiku-4-5-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = parse_ai_response(response.content[0].text)
        processing_time = int((time.time() - start_time) * 1000)
        
        return FinancialsResponse(
            success=True,
            financials=result,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Financial model generation failed: {e}")
        return FinancialsResponse(
            success=False,
            error=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )


@router.post("/pitch-deck", response_model=PitchDeckResponse)
async def generate_pitch_deck(request: PitchDeckRequest, db: Session = Depends(get_db)):
    """Generate investor pitch deck content using AI."""
    start_time = time.time()
    
    client = get_anthropic_client()
    if not client:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        prompt = f"""Generate investor pitch deck content:

COMPANY DETAILS:
- Name: {request.company_name}
- One-line Pitch: {request.one_line_pitch}
- Funding Stage: {request.funding_stage}
- Amount Raising: ${request.amount_raising or 500000:,.0f}
- Description: {request.business_description or 'Not provided'}

Create a comprehensive JSON pitch deck with slides:
1. "cover": {{
   "title": "company name",
   "tagline": "compelling tagline",
   "founding_year": "year or TBD"
}}
2. "problem": {{
   "headline": "problem statement headline",
   "pain_points": ["pain1", "pain2", "pain3"],
   "current_solutions": "how people solve it now",
   "why_now": "why this is urgent now"
}}
3. "solution": {{
   "headline": "solution headline",
   "description": "how we solve the problem",
   "key_features": ["feature1", "feature2", "feature3"],
   "demo_points": "what to show in demo"
}}
4. "market_size": {{
   "tam": "total addressable market",
   "sam": "serviceable addressable market",
   "som": "serviceable obtainable market",
   "growth_rate": "market growth rate"
}}
5. "business_model": {{
   "revenue_streams": ["stream1", "stream2"],
   "pricing": "pricing strategy",
   "unit_economics": "CAC, LTV, margins"
}}
6. "traction": {{
   "key_metrics": ["metric1", "metric2", "metric3"],
   "growth": "month-over-month or milestones",
   "notable_customers": "logos or names if applicable",
   "testimonials": "customer quote if available"
}}
7. "competition": {{
   "competitors": ["comp1", "comp2", "comp3"],
   "differentiation": "what makes us different",
   "competitive_advantages": ["advantage1", "advantage2"]
}}
8. "team": {{
   "why_us": "why this team can win",
   "key_members": ["founder backgrounds"],
   "advisors": "notable advisors if any",
   "hiring_plan": "key roles to fill"
}}
9. "financials": {{
   "revenue_current": "current revenue if any",
   "revenue_projection": "3-year projection",
   "key_assumptions": ["assumption1", "assumption2"]
}}
10. "ask": {{
   "amount": "${request.amount_raising or 500000:,.0f}",
   "use_of_funds": [{{"category": "name", "percentage": pct, "description": "what for"}}],
   "milestones": ["what this funding will achieve"],
   "timeline": "expected timeline for milestones"
}}

Make it compelling and investor-ready. Respond only with valid JSON."""

        response = client.messages.create(
            model="claude-haiku-4-5-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = parse_ai_response(response.content[0].text)
        processing_time = int((time.time() - start_time) * 1000)
        
        return PitchDeckResponse(
            success=True,
            pitch_deck=result,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Pitch deck generation failed: {e}")
        return PitchDeckResponse(
            success=False,
            error=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
