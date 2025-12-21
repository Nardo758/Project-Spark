from fastapi import APIRouter, Request, Header, HTTPException, Depends
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.webhook_gateway import WebhookGateway, WebhookValidationError, RateLimitExceededError
from app.services.geographic_extractor import GeographicExtractor

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


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
