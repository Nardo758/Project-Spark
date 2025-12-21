import hashlib
import hmac
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.scraped_source import ScrapedSource, SourceType
from app.models.rate_limit import RateLimitCounter

logger = logging.getLogger(__name__)


class WebhookValidationError(Exception):
    """Raised when webhook validation fails"""
    pass


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded - should return HTTP 429"""
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class WebhookGateway:
    """
    Webhook Gateway with HMAC authentication for 6 data sources.
    Implements 4-stage validation pipeline:
    1. HMAC signature verification
    2. Schema validation
    3. Deduplication check
    4. Rate limiting
    """

    SUPPORTED_SOURCES = {
        "google_maps": SourceType.google_maps,
        "yelp": SourceType.yelp,
        "reddit": SourceType.reddit,
        "twitter": SourceType.twitter,
        "nextdoor": SourceType.nextdoor,
        "custom": SourceType.custom,
    }

    REQUIRED_FIELDS = {
        "google_maps": ["place_id", "name", "location"],
        "yelp": ["business_id", "name", "coordinates"],
        "reddit": ["post_id", "subreddit", "title"],
        "twitter": ["tweet_id", "text"],
        "nextdoor": ["post_id", "neighborhood"],
        "custom": ["id", "data"],
    }

    def __init__(self, db: Session):
        self.db = db
        self.is_dev_mode = os.getenv("WEBHOOK_DEV_MODE", "0") == "1"
        self.webhook_secret = os.getenv("WEBHOOK_SECRET")
        
        if not self.webhook_secret:
            if self.is_dev_mode:
                self.webhook_secret = "dev-mode-secret"
                logger.debug("Using dev mode webhook secret")
            else:
                raise ValueError(
                    "WEBHOOK_SECRET environment variable is required for production. "
                    "Set WEBHOOK_DEV_MODE=1 for development testing without signatures."
                )

    def verify_hmac_signature(
        self, 
        payload: bytes, 
        signature: str, 
        source: str
    ) -> bool:
        """Stage 1: Verify HMAC-SHA256 signature"""
        if not signature:
            return False
        
        source_secret = os.getenv(f"WEBHOOK_SECRET_{source.upper()}", self.webhook_secret)
        expected_signature = hmac.new(
            source_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        provided_sig = signature.replace("sha256=", "")
        return hmac.compare_digest(expected_signature, provided_sig)

    def validate_schema(self, source: str, data: Dict[str, Any]) -> bool:
        """Stage 2: Validate required fields exist"""
        required = self.REQUIRED_FIELDS.get(source, [])
        return all(field in data for field in required)

    def check_duplicate(self, source: str, external_id: str) -> bool:
        """Stage 3: Check for duplicate entries"""
        existing = self.db.query(ScrapedSource).filter(
            ScrapedSource.source_type == source,
            ScrapedSource.external_id == external_id
        ).first()
        return existing is not None

    def extract_external_id(self, source: str, data: Dict[str, Any]) -> Optional[str]:
        """Extract the external ID from the payload based on source type"""
        id_fields = {
            "google_maps": "place_id",
            "yelp": "business_id",
            "reddit": "post_id",
            "twitter": "tweet_id",
            "nextdoor": "post_id",
            "custom": "id",
        }
        field = id_fields.get(source, "id")
        return str(data.get(field, "")) if data.get(field) else None

    async def process_webhook(
        self,
        source: str,
        payload: bytes,
        data: Dict[str, Any],
        signature: Optional[str] = None,
        scrape_id: Optional[str] = None,
        skip_hmac: bool = False,
    ) -> Dict[str, Any]:
        """
        Process incoming webhook with 4-stage validation.
        1. HMAC signature verification
        2. Schema validation
        3. Deduplication check (before rate limiting to avoid quota drain)
        4. Rate limiting (only for new, valid items)
        Returns processed result or raises WebhookValidationError.
        """
        if source not in self.SUPPORTED_SOURCES:
            raise WebhookValidationError(f"Unsupported source: {source}")

        if not skip_hmac and not self.verify_hmac_signature(payload, signature or "", source):
            logger.warning(f"HMAC verification failed for source: {source}")
            raise WebhookValidationError("Invalid signature")

        if not self.validate_schema(source, data):
            required = self.REQUIRED_FIELDS.get(source, [])
            raise WebhookValidationError(f"Missing required fields: {required}")

        from sqlalchemy.exc import IntegrityError
        
        external_id = self.extract_external_id(source, data)
        
        rate_limit = self._check_rate_limit_simple(source)
        if rate_limit["exceeded"]:
            logger.warning(f"Rate limit exceeded for source: {source}")
            raise RateLimitExceededError(
                f"Rate limit exceeded for source {source}",
                retry_after=rate_limit.get("retry_after", 60)
            )

        try:
            scraped_source = ScrapedSource(
                external_id=external_id,
                source_type=source,
                scrape_id=scrape_id,
                raw_data=data,
                processed=0,
                received_at=datetime.utcnow(),
            )
            self.db.add(scraped_source)
            self.db.commit()
            self.db.refresh(scraped_source)
        except IntegrityError:
            self.db.rollback()
            logger.info(f"Duplicate entry detected via constraint: {source}/{external_id}")
            return {"status": "duplicate", "external_id": external_id}
        except Exception as e:
            self.db.rollback()
            raise

        logger.info(f"Webhook processed: source={source}, id={scraped_source.id}")

        return {
            "status": "accepted",
            "source_id": scraped_source.id,
            "external_id": external_id,
            "source": source,
        }

    async def process_batch(
        self,
        source: str,
        items: List[Dict[str, Any]],
        scrape_id: Optional[str] = None,
        pre_authenticated: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a batch of items from a single source.
        
        Two-phase processing:
        1. Validation phase: Check schema and duplicates for all items (no quota consumed)
        2. Insertion phase: Reserve quota and insert only valid, non-duplicate items
        
        Args:
            source: The source type (google_maps, yelp, etc.)
            items: List of items to process
            scrape_id: Optional scrape job ID for tracking
            pre_authenticated: If True, HMAC was already verified at router level.
                              If False in production mode, raises error.
        """
        if not pre_authenticated and not self.is_dev_mode:
            raise WebhookValidationError(
                "Batch processing requires pre_authenticated=True in production mode. "
                "HMAC must be verified at the router level before calling process_batch."
            )
        
        results = {
            "accepted": 0,
            "duplicates": 0,
            "errors": 0,
            "rate_limited": 0,
            "items": [],
        }

        valid_items = []
        for item in items:
            if source not in self.SUPPORTED_SOURCES:
                results["errors"] += 1
                results["items"].append({"status": "error", "message": f"Unsupported source: {source}"})
                continue
                
            if not self.validate_schema(source, item):
                required = self.REQUIRED_FIELDS.get(source, [])
                results["errors"] += 1
                results["items"].append({"status": "error", "message": f"Missing required fields: {required}"})
                continue
            
            external_id = self.extract_external_id(source, item)
            if external_id and self.check_duplicate(source, external_id):
                results["duplicates"] += 1
                results["items"].append({"status": "duplicate", "external_id": external_id})
                continue
            
            valid_items.append((item, external_id))
        
        if not valid_items:
            return results
        
        from sqlalchemy.exc import IntegrityError
        
        rate_limit = self._check_rate_limit_simple(source)
        if rate_limit["exceeded"]:
            raise RateLimitExceededError(
                f"Rate limit exceeded for source {source}",
                retry_after=rate_limit.get("retry_after", 60)
            )
        
        remaining_quota = rate_limit.get("remaining", 100)
        
        for i, (item, external_id) in enumerate(valid_items):
            if i >= remaining_quota:
                results["rate_limited"] += len(valid_items) - i
                results["items"].append({
                    "status": "rate_limited",
                    "message": f"{len(valid_items) - i} items skipped due to rate limit"
                })
                break
            
            try:
                scraped_source = ScrapedSource(
                    external_id=external_id,
                    source_type=source,
                    scrape_id=scrape_id,
                    raw_data=item,
                    processed=0,
                    received_at=datetime.utcnow(),
                )
                self.db.add(scraped_source)
                self.db.commit()
                self.db.refresh(scraped_source)
                
                results["accepted"] += 1
                results["items"].append({
                    "status": "accepted",
                    "source_id": scraped_source.id,
                    "external_id": external_id,
                })
            except IntegrityError:
                self.db.rollback()
                results["duplicates"] += 1
                results["items"].append({"status": "duplicate", "external_id": external_id})
            except Exception as e:
                self.db.rollback()
                results["errors"] += 1
                results["items"].append({"status": "error", "message": str(e)})

        return results
    
    async def _process_batch_item(
        self,
        source: str,
        data: Dict[str, Any],
        scrape_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a single item in a batch (HMAC already verified at batch level)"""
        if source not in self.SUPPORTED_SOURCES:
            raise WebhookValidationError(f"Unsupported source: {source}")

        if not self.validate_schema(source, data):
            required = self.REQUIRED_FIELDS.get(source, [])
            raise WebhookValidationError(f"Missing required fields: {required}")

        external_id = self.extract_external_id(source, data)
        if external_id and self.check_duplicate(source, external_id):
            return {"status": "duplicate", "external_id": external_id}

        scraped_source = ScrapedSource(
            external_id=external_id,
            source_type=source,
            scrape_id=scrape_id,
            raw_data=data,
            processed=0,
            received_at=datetime.utcnow(),
        )
        self.db.add(scraped_source)
        self.db.commit()
        self.db.refresh(scraped_source)

        return {
            "status": "accepted",
            "source_id": scraped_source.id,
            "external_id": external_id,
        }
    
    def _check_rate_limit_simple(self, source: str) -> Dict[str, Any]:
        """
        Stage 4: Simple rate limiting based on recent accepted entries.
        
        Counts entries in scraped_sources within the last 60 seconds.
        Quota is naturally consumed when items are successfully inserted.
        Duplicates don't consume quota because they hit the unique constraint.
        
        Configure via WEBHOOK_RATE_LIMIT environment variable (default: 100/minute).
        """
        max_requests_per_window = int(os.getenv("WEBHOOK_RATE_LIMIT", "100"))
        window_start = datetime.utcnow() - timedelta(seconds=60)
        
        recent_count = self.db.query(ScrapedSource).filter(
            ScrapedSource.source_type == source,
            ScrapedSource.received_at >= window_start
        ).count()
        
        if recent_count >= max_requests_per_window:
            return {"exceeded": True, "retry_after": 60}
        
        return {"exceeded": False, "remaining": max_requests_per_window - recent_count}

    def _reserve_rate_limit_slot(self, source: str, slots: int = 1) -> Dict[str, Any]:
        """
        Stage 4: Atomically reserve rate limit slot(s) within current transaction.
        
        This method does NOT commit - the caller must commit or rollback.
        If the insert succeeds, the slot is reserved as part of the same transaction.
        If the insert fails and rolls back, the slot reservation is also rolled back.
        
        Uses flush() instead of execute() to ensure the operation participates
        in the current SQLAlchemy session transaction.
        
        Args:
            source: The source type to check
            slots: Number of slots to reserve
            
        Returns:
            {"success": True} if slot reserved
            {"success": False, "retry_after": 60} if rate limit exceeded
        """
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError
        
        max_requests_per_window = int(os.getenv("WEBHOOK_RATE_LIMIT", "100"))
        
        now = datetime.utcnow()
        window_start = now.replace(second=0, microsecond=0)
        
        counter = self.db.query(RateLimitCounter).filter(
            RateLimitCounter.source == source,
            RateLimitCounter.window_start == window_start
        ).with_for_update().first()
        
        if counter is None:
            counter = RateLimitCounter(
                source=source,
                window_start=window_start,
                count=slots,
                max_requests=max_requests_per_window
            )
            self.db.add(counter)
            try:
                self.db.flush()
            except IntegrityError:
                self.db.rollback()
                return self._reserve_rate_limit_slot(source, slots)
        else:
            if counter.count + slots > counter.max_requests:
                return {"success": False, "retry_after": 60}
            counter.count += slots
            counter.updated_at = now
            self.db.flush()
        
        return {"success": True}

    def _check_rate_limit_available(self, source: str, slots_needed: int = 1) -> Dict[str, Any]:
        """
        Stage 4: Atomic rate limiting with dedicated counter table.
        
        Uses INSERT ON CONFLICT UPDATE with row-level locking to provide
        atomic rate limiting. Each source/minute window has a counter row
        that is atomically incremented.
        
        Configure via WEBHOOK_RATE_LIMIT environment variable (default: 100/minute).
        
        Args:
            source: The source type to check
            slots_needed: Number of slots needed (for batch processing)
        """
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError
        
        max_requests_per_window = int(os.getenv("WEBHOOK_RATE_LIMIT", "100"))
        
        now = datetime.utcnow()
        window_start = now.replace(second=0, microsecond=0)
        
        try:
            result = self.db.execute(
                text("""
                    INSERT INTO rate_limit_counters (source, window_start, count, max_requests, created_at, updated_at)
                    VALUES (:source, :window_start, :slots, :max_requests, NOW(), NOW())
                    ON CONFLICT (source, window_start) 
                    DO UPDATE SET 
                        count = rate_limit_counters.count + :slots,
                        updated_at = NOW()
                    WHERE rate_limit_counters.count + :slots <= rate_limit_counters.max_requests
                    RETURNING count, max_requests
                """),
                {
                    "source": source, 
                    "window_start": window_start, 
                    "slots": slots_needed,
                    "max_requests": max_requests_per_window
                }
            )
            row = result.fetchone()
            
            if row is None:
                current = self.db.execute(
                    text("""
                        SELECT count, max_requests FROM rate_limit_counters 
                        WHERE source = :source AND window_start = :window_start
                    """),
                    {"source": source, "window_start": window_start}
                ).fetchone()
                remaining = (current[1] - current[0]) if current else 0
                return {"exceeded": True, "retry_after": 60, "remaining": max(0, remaining)}
            
            current_count, max_reqs = row
            remaining = max_reqs - current_count
            
            return {"exceeded": False, "remaining": remaining, "acquired": slots_needed}
            
        except IntegrityError:
            self.db.rollback()
            return {"exceeded": True, "retry_after": 60, "remaining": 0}

    def get_unprocessed_sources(self, limit: int = 100) -> List[ScrapedSource]:
        """Get unprocessed scraped sources for the worker queue"""
        return self.db.query(ScrapedSource).filter(
            ScrapedSource.processed == 0
        ).limit(limit).all()

    def mark_processed(self, source_id: int, error: Optional[str] = None):
        """Mark a source as processed"""
        source = self.db.query(ScrapedSource).filter(
            ScrapedSource.id == source_id
        ).first()
        if source:
            source.processed = 1 if not error else -1
            source.error_message = error
            source.processed_at = datetime.utcnow()
            self.db.commit()
