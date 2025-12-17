#!/usr/bin/env python3
"""Background script to batch process AI analysis"""
import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from anthropic import Anthropic

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

client = Anthropic(
    base_url=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL"),
    api_key=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY")
)

SYSTEM_PROMPT = """You are a market research analyst. Analyze the opportunity and respond in valid JSON only:
{
    "idea_title": "<clear solution concept, max 80 chars>",
    "problem_statement": "<2-3 sentence professional problem statement>",
    "opportunity_score": <int 0-100>,
    "summary": "<one line, max 100 chars>",
    "market_size_estimate": "<range like $50M-$200M>",
    "competition_level": "<low|medium|high>",
    "urgency_level": "<low|medium|high|critical>",
    "target_audience": "<primary demographic>",
    "pain_intensity": <int 1-10>,
    "business_model_suggestions": ["<suggestion>"],
    "competitive_advantages": ["<advantage>"],
    "key_risks": ["<risk>"],
    "next_steps": ["<action>"]
}"""

def analyze_and_update(db, opp_id, title, description, category):
    prompt = f"TITLE: {title}\nDESCRIPTION: {description[:1500] if description else 'N/A'}\nCATEGORY: {category}"
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = response.content[0].text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            data = json.loads(text[start:end])
            
            db.execute(text("""
                UPDATE opportunities SET
                    ai_analyzed = true,
                    ai_analyzed_at = :now,
                    ai_generated_title = :title,
                    ai_problem_statement = :problem,
                    ai_opportunity_score = :score,
                    ai_summary = :summary,
                    ai_market_size_estimate = :market,
                    ai_competition_level = :comp,
                    ai_urgency_level = :urgency,
                    ai_target_audience = :audience,
                    ai_pain_intensity = :pain
                WHERE id = :id
            """), {
                'now': datetime.utcnow(),
                'title': data.get('idea_title', '')[:500],
                'problem': data.get('problem_statement', ''),
                'score': data.get('opportunity_score', 50),
                'summary': data.get('summary', '')[:500],
                'market': data.get('market_size_estimate', 'Unknown'),
                'comp': data.get('competition_level', 'medium'),
                'urgency': data.get('urgency_level', 'medium'),
                'audience': data.get('target_audience', '')[:255],
                'pain': data.get('pain_intensity', 5),
                'id': opp_id
            })
            db.commit()
            return True
    except Exception as e:
        print(f"Error on {opp_id}: {e}")
        db.rollback()
    return False

def main():
    db = SessionLocal()
    
    result = db.execute(text("""
        SELECT id, title, description, category 
        FROM opportunities 
        WHERE ai_generated_title IS NULL 
        ORDER BY id
    """))
    opps = [(r[0], r[1], r[2], r[3]) for r in result]
    
    print(f"Processing {len(opps)} opportunities...")
    
    success = 0
    for i, (id, title, desc, cat) in enumerate(opps, 1):
        print(f"[{i}/{len(opps)}] ID {id}: ", end="", flush=True)
        if analyze_and_update(db, id, title, desc, cat):
            print("OK")
            success += 1
        else:
            print("FAIL")
        time.sleep(0.3)
    
    db.close()
    print(f"\nComplete: {success}/{len(opps)} success")

if __name__ == "__main__":
    main()
