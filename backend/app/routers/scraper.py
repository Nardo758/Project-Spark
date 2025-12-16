"""
Scraper Data Processing API
Upload and analyze Reddit scraper data to extract business opportunities
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import json
import os

from app.db.database import get_db, SessionLocal
from app.models.opportunity import Opportunity
from app.models.user import User
from app.core.dependencies import get_current_admin_user
from app.routers.ai_analysis import analyze_single_opportunity, update_opportunity_with_analysis

router = APIRouter()

PROBLEM_SIGNALS = {
    "i wish there was": 1.0,
    "why doesn't anyone make": 1.0,
    "can someone please build": 1.0,
    "i'd pay for a solution": 0.95,
    "i would pay for": 0.95,
    "shut up and take my money": 0.95,
    "someone needs to make": 0.90,
    "why isn't there": 0.90,
    "there should be": 0.85,
    "so frustrating that": 0.85,
    "i can't believe we still": 0.85,
    "every single time": 0.80,
    "sick and tired of": 0.80,
    "fed up with": 0.80,
    "does anyone else struggle": 0.75,
    "am i the only one who": 0.75,
    "how do you deal with": 0.70,
    "is there a better way": 0.70,
    "there has to be a better": 0.70,
    "is there an app": 0.80,
    "is there a service": 0.80,
    "looking for a solution": 0.75,
}

INTENSITY_MULTIPLIERS = {
    "!!!": 1.2,
    "!!": 1.15,
    "always": 1.1,
    "constantly": 1.1,
    "every single": 1.15,
    "never": 1.1,
    "impossible": 1.15,
    "nightmare": 1.2,
}

TIER_1_SUBREDDITS = ["somebodymakethis", "mildlyinfuriating", "crappydesign", "doesanybodyelse"]
TIER_2_SUBREDDITS = ["entrepreneur", "smallbusiness", "startups", "consulting", "freelance"]

CATEGORY_KEYWORDS = {
    "Money & Finance": ["money", "finance", "bank", "invest", "budget", "tax", "invoice", "payment"],
    "Health & Wellness": ["health", "fitness", "gym", "doctor", "medical", "mental health", "therapy"],
    "Technology": ["app", "software", "tech", "computer", "phone", "device", "automation", "ai"],
    "Work & Productivity": ["work", "productivity", "remote", "office", "meeting", "project", "task"],
    "Home & Living": ["home", "house", "apartment", "rent", "furniture", "clean", "repair"],
    "Transportation": ["car", "drive", "parking", "commute", "transit", "uber", "travel"],
    "Shopping & Services": ["shop", "buy", "order", "delivery", "shipping", "ecommerce"],
    "Education & Learning": ["learn", "course", "education", "school", "tutor", "study"],
}


class AnalysisResult(BaseModel):
    total_posts: int
    valid_opportunities: int
    imported: int
    skipped: int
    opportunities: List[dict]
    ai_analysis_queued: int = 0


def run_ai_analysis_on_opportunities(opportunity_ids: List[int]):
    """Background task to run AI analysis on imported opportunities"""
    db = SessionLocal()
    try:
        for opp_id in opportunity_ids:
            opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
            if opp and not opp.ai_analyzed:
                analysis = analyze_single_opportunity(opp)
                if analysis:
                    update_opportunity_with_analysis(db, opp, analysis)
                    print(f"AI analyzed opportunity {opp_id}: score={opp.ai_opportunity_score}")
    except Exception as e:
        print(f"AI analysis background error: {e}")
    finally:
        db.close()


class OpportunityPreview(BaseModel):
    title: str
    description: str
    category: str
    confidence_score: float
    subreddit: str
    upvotes: int


def calculate_score(text: str, subreddit: str, upvotes: int, comments: int) -> float:
    """Calculate opportunity confidence score"""
    text_lower = text.lower()
    
    max_score = 0.0
    for phrase, score in PROBLEM_SIGNALS.items():
        if phrase in text_lower:
            max_score = max(max_score, score)
    
    if max_score == 0:
        return 0
    
    multiplier = 1.0
    for marker, mult in INTENSITY_MULTIPLIERS.items():
        if marker.lower() in text_lower:
            multiplier = max(multiplier, mult)
    
    score = max_score * multiplier
    
    sub_lower = subreddit.lower() if subreddit else ""
    if sub_lower in TIER_1_SUBREDDITS:
        score += 0.15
    elif sub_lower in TIER_2_SUBREDDITS:
        score += 0.05
    
    if upvotes > 100:
        score += 0.10
    elif upvotes > 50:
        score += 0.07
    elif upvotes > 10:
        score += 0.05
    
    return min(score, 1.0)


def detect_category(text: str) -> str:
    """Detect category based on keywords"""
    text_lower = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for kw in keywords if kw in text_lower)
    if scores:
        best = max(scores, key=scores.get)
        if scores[best] > 0:
            return best
    return "Technology"


def analyze_post(post: dict) -> Optional[dict]:
    """Analyze a single post"""
    title = post.get("title", "") or ""
    body = post.get("body", "") or ""
    full_text = f"{title} {body}"
    
    if len(full_text.strip()) < 20:
        return None
    
    subreddit = post.get("parsedCommunityName", "") or ""
    upvotes = post.get("upVotes", 0) or 0
    comments = post.get("commentsCount", 0) or 0
    
    score = calculate_score(full_text, subreddit, upvotes, comments)
    
    if score < 0.70:
        return None
    
    return {
        "title": title[:200] if title else "Untitled",
        "description": body[:500] if body else title[:500],
        "category": detect_category(full_text),
        "confidence_score": round(score, 2),
        "subreddit": subreddit,
        "upvotes": upvotes,
        "comments": comments,
        "source_url": post.get("postUrl", ""),
    }


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_scraper_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    auto_import: bool = False,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Upload and analyze Reddit scraper data JSON file.
    Optionally auto-import valid opportunities.
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="File must be JSON format")
    
    try:
        content = await file.read()
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="JSON must be an array of posts")
    
    opportunities = []
    for post in data:
        result = analyze_post(post)
        if result:
            opportunities.append(result)
    
    opportunities.sort(key=lambda x: x["confidence_score"], reverse=True)
    
    imported = 0
    skipped = 0
    imported_ids = []
    
    if auto_import:
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        author_id = demo_user.id if demo_user else None
        
        for opp in opportunities:
            title = opp["title"]
            if not title or title == "Untitled":
                skipped += 1
                continue
            
            existing = db.query(Opportunity).filter(Opportunity.title == title).first()
            if existing:
                skipped += 1
                continue
            
            new_opp = Opportunity(
                title=title,
                description=opp["description"],
                category=opp["category"],
                subcategory="Reddit Discovery",
                severity=3,
                validation_count=opp["upvotes"],
                growth_rate=round(opp["confidence_score"] * 20, 1),
                market_size="$10M-$50M",
                geographic_scope="online",
                author_id=author_id,
                is_anonymous=True,
                completion_status="open",
                status="active",
                source_url=opp.get("source_url", ""),
            )
            db.add(new_opp)
            db.flush()
            imported_ids.append(new_opp.id)
            imported += 1
        
        db.commit()
        
        if imported_ids:
            background_tasks.add_task(run_ai_analysis_on_opportunities, imported_ids)
    
    return AnalysisResult(
        total_posts=len(data),
        valid_opportunities=len(opportunities),
        imported=imported,
        skipped=skipped,
        opportunities=opportunities[:50],
        ai_analysis_queued=len(imported_ids)
    )


@router.get("/stats")
async def get_scraper_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Get statistics about imported scraper data"""
    reddit_opps = db.query(Opportunity).filter(
        Opportunity.subcategory == "Reddit Discovery"
    ).count()
    
    total_opps = db.query(Opportunity).count()
    
    return {
        "reddit_imported": reddit_opps,
        "total_opportunities": total_opps,
        "reddit_percentage": round(reddit_opps / total_opps * 100, 1) if total_opps > 0 else 0
    }
