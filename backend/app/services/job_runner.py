from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.job_run import JobRun
from app.models.transaction import Transaction, TransactionStatus, TransactionType

logger = logging.getLogger(__name__)

_started = False


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _safe_json_loads(s: str | None) -> dict:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


def _safe_json_dumps(obj: Any) -> str | None:
    try:
        return json.dumps(obj)
    except Exception:
        return None


def _start_run(db: Session, job_name: str) -> JobRun:
    run = JobRun(job_name=job_name, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def _finish_run(db: Session, run: JobRun, *, status: str, details: Any | None = None, error: str | None = None) -> None:
    run.status = status
    run.finished_at = _utcnow()
    run.details_json = _safe_json_dumps(details) if details is not None else None
    run.error = error
    db.add(run)
    db.commit()


async def _run_job(job_name: str, coro: Callable[[Session], Awaitable[dict]]) -> None:
    db = SessionLocal()
    run = None
    try:
        run = _start_run(db, job_name)
        details = await coro(db)
        _finish_run(db, run, status="succeeded", details=details)
    except Exception as e:
        logger.exception("Job %s failed", job_name)
        if run is not None:
            try:
                _finish_run(db, run, status="failed", error=str(e))
            except Exception:
                try:
                    db.rollback()
                except Exception:
                    pass
    finally:
        db.close()


async def _escrow_release_job(db: Session) -> dict:
    """
    Release escrow-held SUCCESS_FEE transactions when their escrow_release_date has passed.

    Current behavior: mark escrow transaction status from PENDING -> SUCCEEDED and stamp released_at in metadata.
    (Actual Stripe Connect payouts are a future upgrade.)
    """
    now = _utcnow()
    q = db.query(Transaction).filter(
        Transaction.type == TransactionType.SUCCESS_FEE,
        Transaction.status == TransactionStatus.PENDING,
    )
    candidates = q.order_by(Transaction.created_at.asc()).limit(500).all()

    released = 0
    skipped = 0
    checked = 0

    for tx in candidates:
        checked += 1
        meta = _safe_json_loads(tx.metadata_json)
        if meta.get("split_type") != "escrow_share":
            skipped += 1
            continue

        release_at_raw = meta.get("escrow_release_date")
        if not release_at_raw:
            skipped += 1
            continue

        try:
            release_at = datetime.fromisoformat(release_at_raw.replace("Z", "+00:00"))
            if release_at.tzinfo is None:
                release_at = release_at.replace(tzinfo=timezone.utc)
        except Exception:
            skipped += 1
            continue

        if release_at > now:
            continue

        tx.status = TransactionStatus.SUCCEEDED
        meta["released_at"] = now.isoformat()
        tx.metadata_json = _safe_json_dumps(meta) or tx.metadata_json
        db.add(tx)
        released += 1

    if released:
        db.commit()

    return {"checked": checked, "released": released, "skipped": skipped}


async def _apify_import_and_analyze_job(db: Session) -> dict:
    """
    Fetch latest Apify dataset, import new opportunities, then run AI analysis batch.
    """
    from app.routers.webhook import fetch_latest_apify_data
    from app.routers.ai_analysis import analyze_batch, BatchAnalysisRequest

    actor_id = settings.APIFY_ACTOR_ID
    import_result = await fetch_latest_apify_data(db=db, actor_id=actor_id)

    analyzed = None
    if settings.AI_ANALYSIS_JOB_ENABLED:
        try:
            analyzed = await analyze_batch(BatchAnalysisRequest(limit=settings.AI_ANALYSIS_BATCH_SIZE), db=db)
        except Exception as e:
            analyzed = {"error": str(e)}

    return {"actor_id": actor_id, "import": import_result, "analysis": analyzed}


async def _loop(job_name: str, interval_seconds: int, fn: Callable[[Session], Awaitable[dict]]) -> None:
    # Stagger initial run slightly so startup can settle.
    await asyncio.sleep(3)
    while True:
        await _run_job(job_name, fn)
        await asyncio.sleep(max(5, int(interval_seconds)))


def start_background_jobs() -> None:
    """
    Called at app startup. Spawns asyncio tasks for enabled jobs.
    """
    global _started
    if _started:
        return
    _started = True

    if not settings.JOBS_ENABLED:
        logger.info("Background jobs disabled via JOBS_ENABLED=false")
        return

    loop = asyncio.get_event_loop()

    if settings.ESCROW_RELEASE_JOB_ENABLED:
        loop.create_task(_loop("escrow_release", settings.ESCROW_RELEASE_JOB_INTERVAL_SECONDS, _escrow_release_job))
        logger.info("Started job: escrow_release")

    if settings.APIFY_IMPORT_JOB_ENABLED:
        loop.create_task(_loop("apify_import_and_analyze", settings.APIFY_IMPORT_JOB_INTERVAL_SECONDS, _apify_import_and_analyze_job))
        logger.info("Started job: apify_import_and_analyze")

