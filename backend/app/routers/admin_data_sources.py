import secrets
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import case, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin_user
from app.db.database import get_db
from app.models.data_source_config import DataSourceConfig
from app.models.scraped_source import ScrapedSource
from app.schemas.admin_data_sources import (
    AdminDataSourceConfig,
    AdminDataSourceStats,
    AdminDataSourceUpdate,
    AdminRotateSecretResponse,
)
from app.services.audit import log_event
from app.services.webhook_gateway import WebhookGateway


router = APIRouter()


def _default_display_name(source: str) -> str:
    mapping = {
        "google_maps": "Google Maps",
        "yelp": "Yelp",
        "reddit": "Reddit",
        "twitter": "Twitter / X",
        "nextdoor": "Nextdoor",
        "custom": "Custom",
    }
    return mapping.get(source, source)


def _get_or_create_config(db: Session, source: str) -> DataSourceConfig:
    cfg = db.query(DataSourceConfig).filter(DataSourceConfig.source == source).first()
    if cfg:
        return cfg
    cfg = DataSourceConfig(
        source=source,
        display_name=_default_display_name(source),
        is_enabled=True,
        rate_limit_per_minute=100,
        hmac_secret=None,
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


@router.get("/data-sources", response_model=List[AdminDataSourceConfig])
def list_data_sources(
    admin_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    supported = list(WebhookGateway.SUPPORTED_SOURCES.keys())

    # Best-effort: if the table doesn't exist yet, return env-based defaults so
    # the UI can still render.
    try:
        configs = db.query(DataSourceConfig).all()
    except SQLAlchemyError:
        configs = []
        table_missing = True
    except Exception:
        configs = []
        table_missing = True
    else:
        table_missing = False

    cfg_by_source = {c.source: c for c in configs}

    if not table_missing:
        # Ensure a row exists for each supported source (idempotent).
        created_any = False
        for s in supported:
            if s not in cfg_by_source:
                cfg = DataSourceConfig(
                    source=s,
                    display_name=_default_display_name(s),
                    is_enabled=True,
                    rate_limit_per_minute=100,
                )
                db.add(cfg)
                cfg_by_source[s] = cfg
                created_any = True
        if created_any:
            db.commit()

    cutoff = datetime.utcnow() - timedelta(hours=24)

    stats_rows = (
        db.query(
            ScrapedSource.source_type.label("source"),
            func.count(ScrapedSource.id).label("received_last_24h"),
            func.sum(case((ScrapedSource.processed == 0, 1), else_=0)).label("pending_count"),
            func.sum(case((ScrapedSource.processed == -1, 1), else_=0)).label("error_count"),
            func.max(ScrapedSource.received_at).label("last_received_at"),
            func.max(ScrapedSource.processed_at).label("last_processed_at"),
        )
        .filter(ScrapedSource.received_at >= cutoff)
        .group_by(ScrapedSource.source_type)
        .all()
    )
    stats_by_source = {
        r.source: AdminDataSourceStats(
            received_last_24h=int(r.received_last_24h or 0),
            pending_count=int(r.pending_count or 0),
            error_count=int(r.error_count or 0),
            last_received_at=r.last_received_at,
            last_processed_at=r.last_processed_at,
        )
        for r in stats_rows
    }

    result: List[AdminDataSourceConfig] = []
    for s in supported:
        cfg = cfg_by_source.get(s)
        result.append(
            AdminDataSourceConfig(
                source=s,
                display_name=(cfg.display_name if cfg and cfg.display_name else _default_display_name(s)),
                is_enabled=True if cfg is None else bool(cfg.is_enabled),
                rate_limit_per_minute=100 if cfg is None else int(cfg.rate_limit_per_minute or 100),
                has_secret=bool(getattr(cfg, "hmac_secret", None)) if cfg is not None else False,
                stats=stats_by_source.get(s, AdminDataSourceStats()),
            )
        )
    return result


@router.patch("/data-sources/{source}", response_model=AdminDataSourceConfig)
def update_data_source(
    source: str,
    payload: AdminDataSourceUpdate,
    request: Request,
    admin_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    if source not in WebhookGateway.SUPPORTED_SOURCES:
        raise HTTPException(status_code=404, detail="Unknown source")

    try:
        cfg = _get_or_create_config(db, source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load source config: {e}")

    data = payload.dict(exclude_unset=True)
    secret_touched = False

    if "display_name" in data:
        cfg.display_name = data["display_name"]
    if "is_enabled" in data and data["is_enabled"] is not None:
        cfg.is_enabled = bool(data["is_enabled"])
    if "rate_limit_per_minute" in data and data["rate_limit_per_minute"] is not None:
        cfg.rate_limit_per_minute = int(data["rate_limit_per_minute"])
    if "hmac_secret" in data:
        secret_touched = True
        incoming = data["hmac_secret"]
        cfg.hmac_secret = None if incoming == "" else incoming

    db.commit()
    db.refresh(cfg)

    log_event(
        db,
        action="admin.data_source.update",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="data_source",
        resource_id=source,
        metadata={
            "fields": list(data.keys()),
            "secret_updated": secret_touched,
        },
    )

    # Stats are filled by list endpoint; return with zeroed stats here.
    return AdminDataSourceConfig(
        source=cfg.source,
        display_name=cfg.display_name,
        is_enabled=bool(cfg.is_enabled),
        rate_limit_per_minute=int(cfg.rate_limit_per_minute or 100),
        has_secret=bool(cfg.hmac_secret),
        stats=AdminDataSourceStats(),
    )


@router.post("/data-sources/{source}/rotate-secret", response_model=AdminRotateSecretResponse)
def rotate_data_source_secret(
    source: str,
    request: Request,
    admin_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    if source not in WebhookGateway.SUPPORTED_SOURCES:
        raise HTTPException(status_code=404, detail="Unknown source")

    cfg = _get_or_create_config(db, source)
    new_secret = secrets.token_urlsafe(32)
    cfg.hmac_secret = new_secret
    db.commit()

    # Never store secrets in logs.
    log_event(
        db,
        action="admin.data_source.rotate_secret",
        actor=admin_user,
        actor_type="admin",
        request=request,
        resource_type="data_source",
        resource_id=source,
        metadata={"rotated": True},
    )

    return {"source": source, "hmac_secret": new_secret}


@router.get("/data-sources/recent")
def list_recent_ingestion(
    source: Optional[str] = Query(None),
    processed: Optional[int] = Query(None, description="0 pending, 1 processed, -1 error"),
    limit: int = Query(50, ge=1, le=200),
    admin_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    q = db.query(ScrapedSource)
    if source:
        q = q.filter(ScrapedSource.source_type == source)
    if processed is not None:
        q = q.filter(ScrapedSource.processed == processed)
    items = q.order_by(ScrapedSource.received_at.desc()).limit(limit).all()
    return {
        "items": [
            {
                "id": s.id,
                "source_type": s.source_type,
                "external_id": s.external_id,
                "scrape_id": s.scrape_id,
                "processed": s.processed,
                "error_message": s.error_message,
                "received_at": s.received_at,
                "processed_at": s.processed_at,
            }
            for s in items
        ]
    }


@router.post("/data-sources/process/opportunities")
async def admin_process_opportunities(
    limit: int = Query(50, ge=1, le=500),
    admin_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    from app.services.opportunity_processor import get_opportunity_processor

    processor = get_opportunity_processor(db)
    return await processor.process_pending_sources(limit=limit)


@router.post("/data-sources/process/geography")
async def admin_process_geography(
    limit: int = Query(100, ge=1, le=1000),
    admin_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    from app.services.geographic_extractor import GeographicExtractor

    extractor = GeographicExtractor(db)
    return await extractor.process_pending_sources(limit=limit)

