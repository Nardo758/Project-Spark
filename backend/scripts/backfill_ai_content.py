#!/usr/bin/env python3
"""
Backfill script to populate AI-generated content for all opportunities.
- Generates raw_source_data from existing fields
- Calls AI analysis to generate ai_generated_title and ai_problem_statement
"""

import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from anthropic import Anthropic

from app.models.opportunity import Opportunity

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

client = Anthropic(
    base_url=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL"),
    api_key=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY")
)

ANALYSIS_SYSTEM_PROMPT = """You are a market research analyst for OppGrid, a platform that identifies business opportunities from real consumer pain points.

Analyze the given raw data and provide a structured assessment. Your job is to:
1. Define a clear, compelling IDEA title (what solution could address this pain)
2. Write a professional PROBLEM STATEMENT describing the core issue
3. Provide market analysis and scoring

Respond in valid JSON format only with the following structure:
{
    "idea_title": "<clear, compelling idea name, max 80 chars - describe the solution concept>",
    "problem_statement": "<2-3 sentence professional problem statement explaining the pain point and why it matters>",
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
}"""

def generate_raw_source_data(opp: Opportunity) -> dict:
    """Generate raw_source_data from existing opportunity fields"""
    return {
        "original_title": opp.title or "",
        "original_body": opp.description or "",
        "subreddit": f"r/{opp.category.lower().replace(' ', '_').replace('&', 'and')}" if opp.category else "r/business",
        "upvotes": opp.validation_count or 0,
        "comments": max(1, (opp.validation_count or 0) // 3),
        "author": "reddit_user",
        "created_utc": opp.created_at.timestamp() if opp.created_at else datetime.now().timestamp(),
        "url": opp.source_url or "",
        "platform": opp.source_platform or "reddit",
        "confidence_score": 0.85
    }

def analyze_opportunity(opp: Opportunity) -> dict:
    """Call Anthropic API to analyze opportunity"""
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
            model="claude-sonnet-4-5",
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
        print(f"  API Error: {e}")
        return None

def update_opportunity(db, opp: Opportunity, analysis: dict):
    """Update opportunity with analysis results"""
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
    
    if analysis.get("idea_title"):
        opp.ai_generated_title = analysis.get("idea_title", "")[:500]
    
    if analysis.get("problem_statement"):
        opp.ai_problem_statement = analysis.get("problem_statement", "")
    
    if not opp.market_size and analysis.get("market_size_estimate"):
        opp.market_size = analysis.get("market_size_estimate", "")
    
    db.commit()

def backfill_opportunity(db, opp: Opportunity) -> bool:
    """Backfill a single opportunity with AI content"""
    try:
        if not opp.raw_source_data:
            raw_data = generate_raw_source_data(opp)
            opp.raw_source_data = json.dumps(raw_data)
            db.commit()
        
        if not opp.ai_generated_title or not opp.ai_problem_statement:
            analysis = analyze_opportunity(opp)
            
            if analysis:
                update_opportunity(db, opp, analysis)
                return True
            else:
                return False
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        db.rollback()
        return False

def main():
    print("=" * 60)
    print("BACKFILL AI CONTENT FOR ALL OPPORTUNITIES")
    print("=" * 60)
    
    db = SessionLocal()
    
    opportunities = db.query(Opportunity).order_by(Opportunity.id).all()
    total = len(opportunities)
    
    print(f"\nFound {total} opportunities to process")
    
    needs_raw_data = sum(1 for o in opportunities if not o.raw_source_data)
    needs_ai = sum(1 for o in opportunities if not o.ai_generated_title or not o.ai_problem_statement)
    
    print(f"  - Need raw_source_data: {needs_raw_data}")
    print(f"  - Need AI content: {needs_ai}")
    print()
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, opp in enumerate(opportunities, 1):
        needs_update = (not opp.raw_source_data or 
                       not opp.ai_generated_title or 
                       not opp.ai_problem_statement)
        
        if not needs_update:
            skipped_count += 1
            print(f"[{i}/{total}] ID {opp.id}: Skipped (already complete)")
            continue
        
        print(f"[{i}/{total}] ID {opp.id}: {opp.title[:50]}...")
        
        if backfill_opportunity(db, opp):
            success_count += 1
            print(f"  ✓ Updated successfully")
        else:
            error_count += 1
            print(f"  ✗ Failed")
        
        time.sleep(0.3)
    
    db.close()
    
    print()
    print("=" * 60)
    print("BACKFILL COMPLETE")
    print("=" * 60)
    print(f"  Success: {success_count}")
    print(f"  Errors:  {error_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total:   {total}")

if __name__ == "__main__":
    main()
