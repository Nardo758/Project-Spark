from fastapi import APIRouter, Request, Header, HTTPException, Depends
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx
import logging

from app.db.database import get_db
from app.services.webhook_gateway import WebhookGateway, WebhookValidationError, RateLimitExceededError
from app.services.geographic_extractor import GeographicExtractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
apify_router = APIRouter(prefix="/webhook", tags=["apify-webhook"])


class WebhookPayload(BaseModel):
    data: Dict[str, Any]
    scrape_id: Optional[str] = None


class BatchWebhookPayload(BaseModel):
    items: List[Dict[str, Any]]
    scrape_id: Optional[str] = None


@router.post("/{source}")
async def receive_webhook(
    source: str,
    payload: WebhookPayload,
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_webhook_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Receive webhook from external scrapers.
    Supports HMAC-SHA256 authentication via X-Hub-Signature-256 or X-Webhook-Signature headers.
    In development mode (WEBHOOK_DEV_MODE=1), HMAC verification can be skipped.
    """
    import os
    gateway = WebhookGateway(db)
    
    signature = x_hub_signature_256 or x_webhook_signature
    
    body = await request.body()
    
    skip_hmac = os.getenv("WEBHOOK_DEV_MODE", "0") == "1"
    
    try:
        result = await gateway.process_webhook(
            source=source,
            payload=body,
            data=payload.data,
            signature=signature,
            scrape_id=payload.scrape_id,
            skip_hmac=skip_hmac,
        )
        return result
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=429,
            detail=str(e),
            headers={"Retry-After": str(e.retry_after)}
        )
    except WebhookValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{source}/batch")
async def receive_batch_webhook(
    source: str,
    payload: BatchWebhookPayload,
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_webhook_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Receive batch webhook with multiple items from a single source.
    Useful for bulk imports from scraping jobs.
    Requires HMAC-SHA256 authentication in production.
    """
    import os
    
    skip_hmac = os.getenv("WEBHOOK_DEV_MODE", "0") == "1"
    
    if not skip_hmac:
        signature = x_hub_signature_256 or x_webhook_signature
        if not signature:
            raise HTTPException(status_code=401, detail="Missing signature header")
        
        body = await request.body()
        gateway = WebhookGateway(db)
        if not gateway.verify_hmac_signature(body, signature, source):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    gateway = WebhookGateway(db)
    
    try:
        result = await gateway.process_batch(
            source=source,
            items=payload.items,
            scrape_id=payload.scrape_id,
            pre_authenticated=True,
        )
        return result
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=429,
            detail=str(e),
            headers={"Retry-After": str(e.retry_after)}
        )
    except WebhookValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/queue/process")
async def process_pending_sources(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Process pending scraped sources and extract geographic features.
    This is typically called by a background worker.
    """
    extractor = GeographicExtractor(db)
    result = await extractor.process_pending_sources(limit=limit)
    return result


@router.get("/sources/pending")
async def get_pending_sources(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get list of unprocessed scraped sources"""
    gateway = WebhookGateway(db)
    sources = gateway.get_unprocessed_sources(limit=limit)
    return {
        "count": len(sources),
        "sources": [
            {
                "id": s.id,
                "source_type": s.source_type,
                "external_id": s.external_id,
                "received_at": s.received_at.isoformat() if s.received_at else None,
            }
            for s in sources
        ],
    }


@router.get("/calendar")
async def get_calendar_data(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """
    Get webhook run data grouped by date and source for calendar display.
    Returns counts per day per source type for the last N days.
    """
    from sqlalchemy import func, text
    from datetime import datetime, timedelta
    from app.models.scraped_source import ScrapedSource
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        func.date(ScrapedSource.received_at).label("run_date"),
        ScrapedSource.source_type,
        func.count().label("count")
    ).filter(
        ScrapedSource.received_at >= cutoff_date
    ).group_by(
        func.date(ScrapedSource.received_at),
        ScrapedSource.source_type
    ).order_by(
        func.date(ScrapedSource.received_at).desc()
    ).all()
    
    calendar_data = {}
    source_totals = {}
    
    for row in results:
        date_str = row.run_date.isoformat() if row.run_date else None
        if date_str:
            if date_str not in calendar_data:
                calendar_data[date_str] = {}
            calendar_data[date_str][row.source_type] = row.count
            source_totals[row.source_type] = source_totals.get(row.source_type, 0) + row.count
    
    total_sources = db.query(func.count()).select_from(ScrapedSource).filter(
        ScrapedSource.received_at >= cutoff_date
    ).scalar()
    
    return {
        "days": days,
        "calendar": calendar_data,
        "source_totals": source_totals,
        "total_items": total_sources or 0,
        "sources": list(source_totals.keys())
    }


@apify_router.post("/apify")
async def receive_apify_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Receive webhook from Apify when an actor run completes.
    Apify sends run metadata with dataset URL - we fetch the data and process it.
    """
    import os
    
    try:
        body = await request.json()
        logger.info(f"Received Apify webhook: {body.get('eventType', 'unknown')}")
        
        resource = body.get("resource", {})
        dataset_id = resource.get("defaultDatasetId")
        actor_id = resource.get("actId", "")
        run_id = resource.get("id", "")
        
        if not dataset_id:
            logger.warning(f"No dataset ID in Apify webhook. Body: {body}")
            raise HTTPException(status_code=400, detail="No datasetId provided")
        
        # Detect source type from actor ID
        source_type = "custom"  # Default to custom for unknown actors
        actor_lower = actor_id.lower()
        if "twitter" in actor_lower or "tweet" in actor_lower:
            source_type = "twitter"
        elif "reddit" in actor_lower:
            source_type = "reddit"
        elif "yelp" in actor_lower:
            source_type = "yelp"
        elif "google" in actor_lower or "maps" in actor_lower:
            source_type = "google_maps"
        elif "craigslist" in actor_lower or "classifieds" in actor_lower:
            source_type = "craigslist"
        
        logger.info(f"Detected source type: {source_type} from actor: {actor_id}")
        
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json&clean=true&limit=1000"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(dataset_url)
            response.raise_for_status()
            items = response.json()
        
        logger.info(f"Fetched {len(items)} items from Apify dataset {dataset_id}")
        
        if not items:
            return {"status": "success", "message": "No items in dataset", "count": 0}
        
        gateway = WebhookGateway(db)
        stats = {"accepted": 0, "duplicates": 0, "errors": 0}
        
        for item in items:
            try:
                result = await gateway.process_webhook(
                    source=source_type,
                    payload=b"{}",
                    data=item,
                    signature=None,
                    scrape_id=run_id,
                    skip_hmac=True,
                )
                if result.get("status") == "accepted":
                    stats["accepted"] += 1
                elif result.get("status") == "duplicate":
                    stats["duplicates"] += 1
                else:
                    stats["errors"] += 1
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                stats["errors"] += 1
        
        logger.info(f"Apify import complete: {stats}")
        return {
            "status": "success",
            "dataset_id": dataset_id,
            "source_type": source_type,
            **stats
        }
        
    except Exception as e:
        logger.error(f"Apify webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
