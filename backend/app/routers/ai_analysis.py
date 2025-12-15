from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
import os
import json
from datetime import datetime

from anthropic import Anthropic

from app.db.database import get_db
from app.models.opportunity import Opportunity

router = APIRouter()

client = Anthropic(
    base_url=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL"),
    api_key=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY")
)

class AnalysisResult(BaseModel):
    opportunity_id: int
    ai_opportunity_score: int
    ai_summary: str
    ai_market_size_estimate: str
    ai_competition_level: str
    ai_urgency_level: str
    ai_target_audience: str
    ai_pain_intensity: int
    ai_business_model_suggestions: List[str]
    ai_competitive_advantages: List[str]
    ai_key_risks: List[str]
    ai_next_steps: List[str]

class BatchAnalysisRequest(BaseModel):
    opportunity_ids: Optional[List[int]] = None
    limit: Optional[int] = 10

class BatchAnalysisResponse(BaseModel):
    processed: int
    failed: int
    results: List[AnalysisResult]

ANALYSIS_SYSTEM_PROMPT = """You are a market research analyst for Katalyst, a platform that identifies business opportunities from real consumer pain points.

Analyze the given problem/opportunity and provide a structured assessment. Be specific and data-driven in your estimates.

Respond in valid JSON format only with the following structure:
{
    "opportunity_score": <int 0-100, higher = better opportunity>,
    "summary": "<one line, max 100 chars, compelling insight for the opportunity>",
    "market_size_estimate": "<range like $50M-$200M, $1B-$5B based on the problem scope>",
    "competition_level": "<low|medium|high>",
    "urgency_level": "<low|medium|high|critical>",
    "target_audience": "<primary demographic, max 100 chars>",
    "pain_intensity": <int 1-10, how painful is this problem>,
    "business_model_suggestions": ["<suggestion 1>", "<suggestion 2>", "<suggestion 3>"],
    "competitive_advantages": ["<advantage 1>", "<advantage 2>"],
    "key_risks": ["<risk 1>", "<risk 2>"],
    "next_steps": ["<action 1>", "<action 2>", "<action 3>"]
}

Scoring guidelines:
- 80-100: Exceptional opportunity - clear pain, large market, low competition
- 60-79: Strong opportunity - validated pain, good market potential
- 40-59: Moderate opportunity - some validation, competitive market
- 20-39: Weak opportunity - unclear pain or saturated market
- 0-19: Poor opportunity - no clear pain or very niche

Consider:
- Validation signals (upvotes/engagement indicate real pain)
- Market size (who else has this problem?)
- Competition (existing solutions and their gaps)
- Timing (is this problem growing or shrinking?)
- Feasibility (can a startup solve this?)"""

def analyze_single_opportunity(opp: Opportunity) -> dict:
    prompt = f"""Analyze this opportunity:

TITLE: {opp.title}

DESCRIPTION: {opp.description[:2000] if opp.description else 'No description'}

CATEGORY: {opp.category}
SUBCATEGORY/SOURCE: {opp.subcategory or 'N/A'}
VALIDATION COUNT (upvotes): {opp.validation_count}
SEVERITY RATING: {opp.severity}/5
GEOGRAPHIC SCOPE: {opp.geographic_scope}

Provide your structured JSON analysis."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=1024,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
        return None
    except Exception as e:
        print(f"Error analyzing opportunity {opp.id}: {e}")
        return None

def update_opportunity_with_analysis(db: Session, opp: Opportunity, analysis: dict):
    opp.ai_analyzed = True
    opp.ai_analyzed_at = datetime.utcnow()
    opp.ai_opportunity_score = analysis.get("opportunity_score", 50)
    opp.ai_summary = analysis.get("summary", "")[:500]
    opp.ai_market_size_estimate = analysis.get("market_size_estimate", "Unknown")
    opp.ai_competition_level = analysis.get("competition_level", "medium")
    opp.ai_urgency_level = analysis.get("urgency_level", "medium")
    opp.ai_target_audience = analysis.get("target_audience", "")[:255]
    opp.ai_pain_intensity = analysis.get("pain_intensity", 5)
    opp.ai_business_model_suggestions = json.dumps(analysis.get("business_model_suggestions", []))
    opp.ai_competitive_advantages = json.dumps(analysis.get("competitive_advantages", []))
    opp.ai_key_risks = json.dumps(analysis.get("key_risks", []))
    opp.ai_next_steps = json.dumps(analysis.get("next_steps", []))
    
    if opp.ai_opportunity_score and not opp.market_size:
        opp.market_size = analysis.get("market_size_estimate", "")
    
    db.commit()

@router.post("/analyze/{opportunity_id}", response_model=AnalysisResult)
async def analyze_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    analysis = analyze_single_opportunity(opp)
    if not analysis:
        raise HTTPException(status_code=500, detail="Failed to analyze opportunity")
    
    update_opportunity_with_analysis(db, opp, analysis)
    
    return AnalysisResult(
        opportunity_id=opp.id,
        ai_opportunity_score=opp.ai_opportunity_score,
        ai_summary=opp.ai_summary,
        ai_market_size_estimate=opp.ai_market_size_estimate,
        ai_competition_level=opp.ai_competition_level,
        ai_urgency_level=opp.ai_urgency_level,
        ai_target_audience=opp.ai_target_audience,
        ai_pain_intensity=opp.ai_pain_intensity,
        ai_business_model_suggestions=json.loads(opp.ai_business_model_suggestions or "[]"),
        ai_competitive_advantages=json.loads(opp.ai_competitive_advantages or "[]"),
        ai_key_risks=json.loads(opp.ai_key_risks or "[]"),
        ai_next_steps=json.loads(opp.ai_next_steps or "[]")
    )

@router.post("/analyze-batch", response_model=BatchAnalysisResponse)
async def analyze_batch(request: BatchAnalysisRequest, db: Session = Depends(get_db)):
    if request.opportunity_ids:
        opportunities = db.query(Opportunity).filter(
            Opportunity.id.in_(request.opportunity_ids)
        ).all()
    else:
        opportunities = db.query(Opportunity).filter(
            Opportunity.ai_analyzed == False
        ).order_by(
            Opportunity.validation_count.desc()
        ).limit(request.limit or 10).all()
    
    results = []
    failed = 0
    
    for opp in opportunities:
        try:
            analysis = analyze_single_opportunity(opp)
            if analysis:
                update_opportunity_with_analysis(db, opp, analysis)
                db.flush()
                results.append(AnalysisResult(
                    opportunity_id=opp.id,
                    ai_opportunity_score=opp.ai_opportunity_score,
                    ai_summary=opp.ai_summary,
                    ai_market_size_estimate=opp.ai_market_size_estimate,
                    ai_competition_level=opp.ai_competition_level,
                    ai_urgency_level=opp.ai_urgency_level,
                    ai_target_audience=opp.ai_target_audience,
                    ai_pain_intensity=opp.ai_pain_intensity,
                    ai_business_model_suggestions=json.loads(opp.ai_business_model_suggestions or "[]"),
                    ai_competitive_advantages=json.loads(opp.ai_competitive_advantages or "[]"),
                    ai_key_risks=json.loads(opp.ai_key_risks or "[]"),
                    ai_next_steps=json.loads(opp.ai_next_steps or "[]")
                ))
            else:
                failed += 1
        except Exception as e:
            print(f"Error processing opportunity {opp.id}: {e}")
            failed += 1
            db.rollback()
            continue
    
    try:
        db.commit()
    except Exception as e:
        print(f"Error committing batch: {e}")
        db.rollback()
    
    return BatchAnalysisResponse(
        processed=len(results),
        failed=failed,
        results=results
    )

@router.get("/top-opportunities")
async def get_top_opportunities(limit: int = 5, db: Session = Depends(get_db)):
    opportunities = db.query(Opportunity).filter(
        Opportunity.ai_analyzed == True,
        Opportunity.ai_opportunity_score.isnot(None)
    ).order_by(
        Opportunity.ai_opportunity_score.desc()
    ).limit(limit).all()
    
    return [{
        "id": opp.id,
        "title": opp.title,
        "category": opp.category,
        "ai_opportunity_score": opp.ai_opportunity_score,
        "ai_summary": opp.ai_summary,
        "ai_market_size_estimate": opp.ai_market_size_estimate,
        "ai_competition_level": opp.ai_competition_level,
        "ai_urgency_level": opp.ai_urgency_level,
        "ai_target_audience": opp.ai_target_audience,
        "validation_count": opp.validation_count,
        "severity": opp.severity
    } for opp in opportunities]

@router.get("/stats")
async def get_analysis_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Opportunity.id)).scalar()
    analyzed = db.query(func.count(Opportunity.id)).filter(
        Opportunity.ai_analyzed == True
    ).scalar()
    
    avg_score = db.query(func.avg(Opportunity.ai_opportunity_score)).filter(
        Opportunity.ai_opportunity_score.isnot(None)
    ).scalar()
    
    high_potential = db.query(func.count(Opportunity.id)).filter(
        Opportunity.ai_opportunity_score >= 70
    ).scalar()
    
    return {
        "total_opportunities": total,
        "analyzed_opportunities": analyzed,
        "pending_analysis": total - analyzed,
        "average_score": round(avg_score, 1) if avg_score else 0,
        "high_potential_count": high_potential
    }
