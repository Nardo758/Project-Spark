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
            model="claude-sonnet-4-20250514",
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
            model="claude-sonnet-4-20250514",
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
            model="claude-sonnet-4-20250514",
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


class FeasibilityRequest(BaseModel):
    business_idea: str = Field(..., min_length=10, max_length=5000)
    industry: Optional[str] = None
    location: Optional[str] = None


class FeasibilityResponse(BaseModel):
    success: bool
    study: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class MarketAnalysisRequest(BaseModel):
    industry: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = None


class MarketAnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class StrategicAssessmentRequest(BaseModel):
    business_concept: str = Field(..., min_length=10, max_length=5000)
    industry: Optional[str] = None
    competition_level: Optional[str] = None


class StrategicAssessmentResponse(BaseModel):
    success: bool
    assessment: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class PestleRequest(BaseModel):
    business_industry: str = Field(..., min_length=2, max_length=200)
    target_region: Optional[str] = None
    description: Optional[str] = None


class PestleResponse(BaseModel):
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


@router.post("/feasibility", response_model=FeasibilityResponse)
async def generate_feasibility_study(request: FeasibilityRequest, db: Session = Depends(get_db)):
    """Generate a feasibility study using AI."""
    start_time = time.time()
    
    client = get_anthropic_client()
    if not client:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        prompt = f"""Conduct a comprehensive feasibility study for this business idea:

BUSINESS IDEA:
{request.business_idea}

Industry: {request.industry or 'To be determined'}
Location: {request.location or 'General market'}

Generate a detailed JSON feasibility study with these sections:
1. "project_overview": {{
   "summary": "brief description of what is being evaluated",
   "scope": "scope of the feasibility analysis",
   "objectives": ["objective1", "objective2", "objective3"]
}}
2. "technical_feasibility": {{
   "score": 1-10,
   "assessment": "can this be built/delivered?",
   "requirements": ["requirement1", "requirement2"],
   "challenges": ["challenge1", "challenge2"],
   "mitigation": "how to address challenges"
}}
3. "market_feasibility": {{
   "score": 1-10,
   "demand_assessment": "is there market demand?",
   "target_market_size": "estimated market size",
   "competition_analysis": "competitive landscape",
   "market_entry_barriers": ["barrier1", "barrier2"]
}}
4. "financial_feasibility": {{
   "score": 1-10,
   "startup_costs": "estimated initial investment",
   "operating_costs": "monthly/annual operating expenses",
   "revenue_potential": "revenue projections",
   "roi_estimate": "expected return on investment",
   "break_even_timeline": "time to break even"
}}
5. "operational_feasibility": {{
   "score": 1-10,
   "execution_plan": "how can this be executed?",
   "resources_needed": ["resource1", "resource2"],
   "team_requirements": ["role1", "role2"],
   "timeline": "implementation timeline"
}}
6. "legal_regulatory": {{
   "score": 1-10,
   "compliance_requirements": ["requirement1", "requirement2"],
   "licenses_permits": ["license1", "license2"],
   "risks": ["risk1", "risk2"]
}}
7. "recommendation": {{
   "overall_score": 1-10,
   "verdict": "GO / NO-GO / CONDITIONAL",
   "justification": "reasoning for recommendation",
   "conditions": ["condition if applicable"],
   "next_steps": ["step1", "step2", "step3"]
}}

Be objective and balanced. Respond only with valid JSON."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = parse_ai_response(response.content[0].text)
        processing_time = int((time.time() - start_time) * 1000)
        
        return FeasibilityResponse(
            success=True,
            study=result,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Feasibility study generation failed: {e}")
        return FeasibilityResponse(
            success=False,
            error=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )


@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def generate_market_analysis(request: MarketAnalysisRequest, db: Session = Depends(get_db)):
    """Generate a comprehensive market analysis using AI."""
    start_time = time.time()
    
    client = get_anthropic_client()
    if not client:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        prompt = f"""Create a comprehensive market analysis for this industry/market:

MARKET/INDUSTRY: {request.industry}
Description: {request.description or 'General analysis'}
Location Focus: {request.location or 'Global/National'}

Generate a detailed JSON market analysis with these sections:
1. "industry_overview": {{
   "definition": "market definition and scope",
   "market_size": "current market size estimate",
   "growth_rate": "annual growth rate",
   "key_drivers": ["driver1", "driver2", "driver3"],
   "market_stage": "emerging/growth/mature/declining"
}}
2. "market_segmentation": {{
   "segments": [
     {{"name": "segment1", "size": "size", "growth": "growth rate", "characteristics": "key traits"}},
     {{"name": "segment2", "size": "size", "growth": "growth rate", "characteristics": "key traits"}}
   ],
   "geographic_distribution": "regional breakdown",
   "highest_potential_segment": "which segment to target"
}}
3. "competitive_landscape": {{
   "major_players": [
     {{"name": "company1", "market_share": "share", "strengths": "key strengths"}},
     {{"name": "company2", "market_share": "share", "strengths": "key strengths"}}
   ],
   "concentration": "fragmented/consolidated",
   "barriers_to_entry": ["barrier1", "barrier2"],
   "market_gaps": ["gap1", "gap2"]
}}
4. "market_trends": {{
   "current_trends": ["trend1", "trend2", "trend3"],
   "emerging_opportunities": ["opportunity1", "opportunity2"],
   "potential_disruptions": ["disruption1", "disruption2"],
   "technology_impact": "how technology is changing the market"
}}
5. "consumer_analysis": {{
   "buyer_behavior": "how customers make purchase decisions",
   "key_purchase_factors": ["factor1", "factor2", "factor3"],
   "price_sensitivity": "low/medium/high",
   "unmet_needs": ["need1", "need2"]
}}
6. "market_forecast": {{
   "projection_3_year": "3-year market size projection",
   "projection_5_year": "5-year market size projection",
   "growth_scenarios": {{
     "optimistic": "best case",
     "base": "expected case",
     "pessimistic": "worst case"
   }},
   "key_assumptions": ["assumption1", "assumption2"],
   "risk_factors": ["risk1", "risk2"]
}}

Include data points and be specific. Respond only with valid JSON."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = parse_ai_response(response.content[0].text)
        processing_time = int((time.time() - start_time) * 1000)
        
        return MarketAnalysisResponse(
            success=True,
            analysis=result,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Market analysis generation failed: {e}")
        return MarketAnalysisResponse(
            success=False,
            error=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )


@router.post("/strategic-assessment", response_model=StrategicAssessmentResponse)
async def generate_strategic_assessment(request: StrategicAssessmentRequest, db: Session = Depends(get_db)):
    """Generate a strategic assessment with SWOT analysis using AI."""
    start_time = time.time()
    
    client = get_anthropic_client()
    if not client:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        prompt = f"""Create a comprehensive strategic assessment for this business concept:

BUSINESS CONCEPT:
{request.business_concept}

Industry: {request.industry or 'To be determined'}
Competition Level: {request.competition_level or 'Unknown'}

Generate a detailed JSON strategic assessment with these sections:
1. "swot_analysis": {{
   "strengths": [
     {{"factor": "strength1", "impact": "high/medium/low", "explanation": "why this matters"}}
   ],
   "weaknesses": [
     {{"factor": "weakness1", "impact": "high/medium/low", "explanation": "why this matters"}}
   ],
   "opportunities": [
     {{"factor": "opportunity1", "impact": "high/medium/low", "explanation": "why this matters"}}
   ],
   "threats": [
     {{"factor": "threat1", "impact": "high/medium/low", "explanation": "why this matters"}}
   ]
}}
2. "strategic_position": {{
   "current_position": "assessment of current market position",
   "competitive_advantages": ["advantage1", "advantage2"],
   "value_proposition_clarity": "clear/needs work/unclear",
   "differentiation": "how this stands out"
}}
3. "growth_strategies": {{
   "market_penetration": {{"strategy": "description", "feasibility": "high/medium/low", "timeline": "short/medium/long"}},
   "market_development": {{"strategy": "description", "feasibility": "high/medium/low", "timeline": "short/medium/long"}},
   "product_expansion": {{"strategy": "description", "feasibility": "high/medium/low", "timeline": "short/medium/long"}},
   "diversification": {{"strategy": "description", "feasibility": "high/medium/low", "timeline": "short/medium/long"}},
   "recommended_approach": "which strategy to prioritize and why"
}}
4. "resource_requirements": {{
   "key_capabilities": ["capability1", "capability2"],
   "investment_needed": "estimated investment range",
   "team_needs": ["role1", "role2"],
   "technology_requirements": ["tech1", "tech2"]
}}
5. "risk_assessment": {{
   "strategic_risks": [
     {{"risk": "risk1", "likelihood": "high/medium/low", "impact": "high/medium/low", "mitigation": "how to address"}}
   ],
   "overall_risk_level": "high/medium/low",
   "contingency_plans": ["plan1", "plan2"]
}}
6. "recommendations": {{
   "priority_actions": [
     {{"action": "action1", "timeline": "0-3 months", "expected_outcome": "result"}}
   ],
   "strategic_initiatives": [
     {{"initiative": "initiative1", "timeline": "3-12 months", "expected_outcome": "result"}}
   ],
   "long_term_vision": "5-year strategic direction",
   "success_metrics": ["metric1", "metric2", "metric3"]
}}

Provide actionable, specific recommendations. Respond only with valid JSON."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = parse_ai_response(response.content[0].text)
        processing_time = int((time.time() - start_time) * 1000)
        
        return StrategicAssessmentResponse(
            success=True,
            assessment=result,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Strategic assessment generation failed: {e}")
        return StrategicAssessmentResponse(
            success=False,
            error=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )


@router.post("/pestle", response_model=PestleResponse)
async def generate_pestle_analysis(request: PestleRequest, db: Session = Depends(get_db)):
    """Generate a PESTLE analysis using AI."""
    start_time = time.time()
    
    client = get_anthropic_client()
    if not client:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        prompt = f"""Conduct a comprehensive PESTLE analysis for:

BUSINESS/INDUSTRY: {request.business_industry}
Target Region: {request.target_region or 'General/National'}
Description: {request.description or 'General analysis'}

Generate a detailed JSON PESTLE analysis with these sections:
1. "political": {{
   "impact_level": "high/medium/low",
   "factors": [
     {{"factor": "Government policies", "description": "relevant policies affecting the business", "implication": "what this means for the business"}},
     {{"factor": "Political stability", "description": "current political climate", "implication": "impact on business operations"}}
   ],
   "key_risks": ["risk1", "risk2"],
   "opportunities": ["opportunity1"]
}}
2. "economic": {{
   "impact_level": "high/medium/low",
   "factors": [
     {{"factor": "Economic growth", "description": "GDP trends and economic outlook", "implication": "impact on market"}},
     {{"factor": "Interest rates", "description": "current interest rate environment", "implication": "effect on financing"}},
     {{"factor": "Consumer spending", "description": "spending patterns", "implication": "demand implications"}}
   ],
   "key_risks": ["risk1", "risk2"],
   "opportunities": ["opportunity1"]
}}
3. "social": {{
   "impact_level": "high/medium/low",
   "factors": [
     {{"factor": "Demographics", "description": "population trends", "implication": "market size implications"}},
     {{"factor": "Cultural attitudes", "description": "relevant cultural trends", "implication": "product/service fit"}},
     {{"factor": "Lifestyle changes", "description": "behavioral shifts", "implication": "demand drivers"}}
   ],
   "key_risks": ["risk1"],
   "opportunities": ["opportunity1", "opportunity2"]
}}
4. "technological": {{
   "impact_level": "high/medium/low",
   "factors": [
     {{"factor": "Technology adoption", "description": "tech adoption rates in target market", "implication": "digital strategy needs"}},
     {{"factor": "Innovation", "description": "relevant innovations", "implication": "competitive implications"}},
     {{"factor": "Digital transformation", "description": "industry digitization", "implication": "operational needs"}}
   ],
   "key_risks": ["disruption risk"],
   "opportunities": ["tech-enabled growth"]
}}
5. "legal": {{
   "impact_level": "high/medium/low",
   "factors": [
     {{"factor": "Industry regulations", "description": "key regulations", "implication": "compliance requirements"}},
     {{"factor": "Employment laws", "description": "labor regulations", "implication": "HR implications"}},
     {{"factor": "Consumer protection", "description": "consumer rights laws", "implication": "product/service requirements"}}
   ],
   "key_risks": ["compliance risk"],
   "opportunities": ["first-mover compliance advantage"]
}}
6. "environmental": {{
   "impact_level": "high/medium/low",
   "factors": [
     {{"factor": "Environmental regulations", "description": "environmental compliance", "implication": "operational requirements"}},
     {{"factor": "Sustainability trends", "description": "green/sustainable trends", "implication": "product positioning"}},
     {{"factor": "Climate impact", "description": "climate considerations", "implication": "long-term planning"}}
   ],
   "key_risks": ["environmental compliance risk"],
   "opportunities": ["green market positioning"]
}}
7. "summary": {{
   "highest_impact_factors": ["factor1", "factor2", "factor3"],
   "critical_risks": ["risk1", "risk2"],
   "key_opportunities": ["opportunity1", "opportunity2"],
   "strategic_implications": "overall strategic guidance based on PESTLE",
   "recommended_actions": ["action1", "action2", "action3"]
}}

Be specific to the industry and region. Respond only with valid JSON."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = parse_ai_response(response.content[0].text)
        processing_time = int((time.time() - start_time) * 1000)
        
        return PestleResponse(
            success=True,
            analysis=result,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"PESTLE analysis generation failed: {e}")
        return PestleResponse(
            success=False,
            error=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
