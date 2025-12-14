from fastapi import APIRouter, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from pydantic import BaseModel
import os
import httpx
from datetime import datetime

from ..db.database import get_db
from ..models.opportunity import Opportunity

router = APIRouter(prefix="/webhook", tags=["webhook"])

APIFY_WEBHOOK_SECRET = os.getenv("APIFY_WEBHOOK_SECRET", "")

class ApifyWebhookPayload(BaseModel):
    runId: Optional[str] = None
    datasetId: Optional[str] = None
    status: Optional[str] = None
    actorId: Optional[str] = None

class RedditPost(BaseModel):
    id: str
    title: Optional[str] = None
    body: Optional[str] = None
    parsedCommunityName: Optional[str] = None
    communityName: Optional[str] = None
    upVotes: Optional[int] = 0
    commentsCount: Optional[int] = 0
    postUrl: Optional[str] = None
    createdAt: Optional[str] = None
    dataType: Optional[str] = None
    
class RedditComment(BaseModel):
    id: str
    body: Optional[str] = None
    subredditName: Optional[str] = None
    commentUpVotes: Optional[int] = 0
    authorName: Optional[str] = None
    postId: Optional[str] = None
    dataType: Optional[str] = None

def categorize_content(title: str, body: str) -> str:
    text = f"{title} {body}".lower()
    
    categories = {
        "Technology & Software": ["app", "software", "code", "api", "developer", "programming", "tech", "ai", "automation"],
        "Health & Wellness": ["health", "medical", "fitness", "mental", "wellness", "doctor", "therapy", "diet"],
        "Money & Finance": ["money", "invest", "budget", "financial", "bank", "crypto", "payment", "subscription"],
        "Home & Living": ["home", "house", "apartment", "rent", "furniture", "cleaning", "maintenance"],
        "Work & Productivity": ["work", "job", "career", "productivity", "meeting", "email", "remote", "office"],
        "Shopping & E-commerce": ["buy", "shop", "product", "ecommerce", "retail", "price", "deal"],
        "Education & Learning": ["learn", "course", "education", "school", "training", "skill", "tutorial"],
        "Entertainment & Media": ["video", "music", "game", "stream", "content", "movie", "entertainment"],
    }
    
    for category, keywords in categories.items():
        if any(kw in text for kw in keywords):
            return category
    
    return "General"

def calculate_severity(upvotes: int, comments: int, body: str) -> int:
    score = 1
    
    if upvotes > 100:
        score += 2
    elif upvotes > 20:
        score += 1
    
    if comments > 50:
        score += 1
    elif comments > 10:
        score += 0.5
    
    frustration_words = ["frustrated", "annoying", "hate", "terrible", "awful", "nightmare", "impossible", "ridiculous"]
    if any(word in body.lower() for word in frustration_words):
        score += 1
    
    return min(5, max(1, int(score)))

def extract_opportunity_from_post(post: dict) -> dict:
    title = post.get("title", "")
    body = post.get("body", "")
    upvotes = post.get("upVotes", 0) or 0
    comments = post.get("commentsCount", 0) or 0
    subreddit = post.get("parsedCommunityName") or post.get("communityName", "").replace("r/", "")
    
    return {
        "title": title[:500] if title else "Untitled Opportunity",
        "description": body[:5000] if body else "",
        "category": categorize_content(title, body),
        "subcategory": subreddit,
        "severity": calculate_severity(upvotes, comments, body),
        "validation_count": upvotes,
        "growth_rate": min(50.0, float(upvotes) / 10) if upvotes else 0.0,
        "geographic_scope": "online",
        "source_url": post.get("postUrl") or post.get("contentUrl"),
        "source_platform": "reddit",
        "source_id": post.get("id"),
    }

@router.post("/apify")
async def receive_apify_webhook(
    payload: ApifyWebhookPayload,
    db: Session = Depends(get_db),
    x_apify_webhook_secret: Optional[str] = Header(None, alias="X-Apify-Webhook-Secret")
):
    if APIFY_WEBHOOK_SECRET and x_apify_webhook_secret != APIFY_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    
    if not payload.datasetId:
        raise HTTPException(status_code=400, detail="No datasetId provided")
    
    apify_token = os.getenv("APIFY_API_TOKEN", "")
    if not apify_token:
        raise HTTPException(status_code=500, detail="APIFY_API_TOKEN not configured")
    
    dataset_url = f"https://api.apify.com/v2/datasets/{payload.datasetId}/items?token={apify_token}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(dataset_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to fetch dataset: {response.text}")
        
        items = response.json()
    
    created_count = 0
    skipped_count = 0
    
    for item in items:
        if item.get("dataType") != "post":
            continue
        
        source_id = item.get("id")
        existing = db.query(Opportunity).filter(Opportunity.source_id == source_id).first()
        if existing:
            skipped_count += 1
            continue
        
        opp_data = extract_opportunity_from_post(item)
        
        opportunity = Opportunity(
            title=opp_data["title"],
            description=opp_data["description"],
            category=opp_data["category"],
            subcategory=opp_data["subcategory"],
            severity=opp_data["severity"],
            validation_count=opp_data["validation_count"],
            growth_rate=opp_data["growth_rate"],
            geographic_scope=opp_data["geographic_scope"],
        )
        
        db.add(opportunity)
        created_count += 1
    
    db.commit()
    
    return {
        "status": "success",
        "runId": payload.runId,
        "created": created_count,
        "skipped": skipped_count,
        "total_items": len(items)
    }

@router.post("/apify/import")
async def import_apify_data(
    data: List[dict],
    db: Session = Depends(get_db),
    x_apify_webhook_secret: Optional[str] = Header(None, alias="X-Apify-Webhook-Secret")
):
    if APIFY_WEBHOOK_SECRET and x_apify_webhook_secret != APIFY_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    
    created_count = 0
    skipped_count = 0
    
    for item in data:
        if item.get("dataType") != "post":
            continue
        
        source_id = item.get("id")
        existing = db.query(Opportunity).filter(Opportunity.source_id == source_id).first()
        if existing:
            skipped_count += 1
            continue
        
        opp_data = extract_opportunity_from_post(item)
        
        opportunity = Opportunity(
            title=opp_data["title"],
            description=opp_data["description"],
            category=opp_data["category"],
            subcategory=opp_data["subcategory"],
            severity=opp_data["severity"],
            validation_count=opp_data["validation_count"],
            growth_rate=opp_data["growth_rate"],
            geographic_scope=opp_data["geographic_scope"],
        )
        
        db.add(opportunity)
        created_count += 1
    
    db.commit()
    
    return {
        "status": "success",
        "created": created_count,
        "skipped": skipped_count,
        "total_items": len(data)
    }
