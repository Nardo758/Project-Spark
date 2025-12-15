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

@router.post("/apify/fetch-latest")
async def fetch_latest_apify_data(
    db: Session = Depends(get_db),
    actor_id: str = "trudax/reddit-scraper-lite"
):
    """Fetch latest data from an Apify actor's default dataset"""
    apify_token = os.getenv("APIFY_API_TOKEN", "")
    if not apify_token:
        raise HTTPException(status_code=500, detail="APIFY_API_TOKEN not configured")
    
    # Get the latest successful run for this actor
    runs_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={apify_token}&status=SUCCEEDED&desc=true&limit=1"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Get latest run
        runs_response = await client.get(runs_url)
        if runs_response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to fetch runs: {runs_response.text}")
        
        runs_data = runs_response.json()
        if not runs_data.get("data", {}).get("items"):
            raise HTTPException(status_code=404, detail="No successful runs found for this actor")
        
        latest_run = runs_data["data"]["items"][0]
        dataset_id = latest_run.get("defaultDatasetId")
        run_id = latest_run.get("id")
        
        if not dataset_id:
            raise HTTPException(status_code=500, detail="No dataset found for this run")
        
        # Fetch the dataset items
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={apify_token}&limit=500"
        dataset_response = await client.get(dataset_url)
        
        if dataset_response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to fetch dataset: {dataset_response.text}")
        
        items = dataset_response.json()
    
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
            source_url=opp_data["source_url"],
            source_platform=opp_data["source_platform"],
            source_id=opp_data["source_id"],
        )
        
        db.add(opportunity)
        created_count += 1
    
    db.commit()
    
    return {
        "status": "success",
        "run_id": run_id,
        "dataset_id": dataset_id,
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


@router.post("/apify/trigger-scrape")
async def trigger_apify_scrape(
    x_apify_webhook_secret: Optional[str] = Header(None, alias="X-Apify-Webhook-Secret")
):
    """Trigger the Apify Reddit scraper to run a new scrape"""
    if APIFY_WEBHOOK_SECRET and x_apify_webhook_secret != APIFY_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    
    apify_token = os.getenv("APIFY_API_TOKEN", "")
    if not apify_token:
        raise HTTPException(status_code=500, detail="APIFY_API_TOKEN not configured")
    
    actor_id = "trudax/reddit-scraper-lite"
    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={apify_token}"
    
    run_input = {
        "debugMode": False,
        "maxItems": 200,
        "maxPostCount": 200,
        "maxComments": 0,
        "proxy": {"useApifyProxy": True},
        "scrollTimeout": 40,
        "searchComments": False,
        "searchCommunities": False,
        "searchPosts": True,
        "searchUsers": False,
        "searches": [
            "frustrated with",
            "wish there was",
            "why is it so hard to",
            "anyone else annoyed by",
            "there should be an app for",
            "I hate how",
            "biggest pain point",
            "looking for solution to"
        ],
        "skipComments": True,
        "sort": "relevance",
        "time": "week"
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(run_url, json=run_input)
        
        if response.status_code != 201:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to trigger scraper: {response.status_code} - {response.text}"
            )
        
        run_data = response.json().get("data", {})
        return {
            "status": "started",
            "run_id": run_data.get("id"),
            "started_at": datetime.now().isoformat(),
            "message": "Scraper started. Use /apify/fetch-latest to import results after completion."
        }
