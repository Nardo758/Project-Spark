from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

logger = logging.getLogger(__name__)

LOCAL_HOSTS = {
    "localhost",
    "127.0.0.1",
    "::1",
    "db",
    "db.internal",
    "db.replit.internal",
}
LOCAL_SUFFIXES = (".internal", ".local")


def _is_local_host(hostname: str) -> bool:
    """Return True when the host points to a local/Postgres instance without SSL."""
    if not hostname:
        return False
    hostname = hostname.lower()
    if hostname in LOCAL_HOSTS or hostname.startswith("127."):
        return True
    return any(hostname.endswith(suffix) for suffix in LOCAL_SUFFIXES)


def _prepare_postgres_url(raw_url: str) -> str:
    """Normalize postgres URL and append sslmode when needed."""
    if not raw_url:
        return raw_url

    normalized = raw_url.replace("postgres://", "postgresql://", 1)
    parsed = urlparse(normalized)

    if not parsed.scheme.startswith("postgres"):
        return normalized

    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    host = parsed.hostname or ""

    if "sslmode" not in query_params:
        if _is_local_host(host):
            logger.info(
                "Detected local PostgreSQL host (%s); skipping sslmode enforcement", host
            )
        else:
            query_params["sslmode"] = "require"

    new_query = urlencode(query_params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def get_database_url():
    """Get PostgreSQL connection URL from PG* environment variables
    
    For Replit: Uses PGHOST, PGDATABASE, PGUSER, PGPASSWORD from .replit file
    These are set to: db:5432/replit with user 'replit'
    
    Note: Ignores DATABASE_URL and POSTGRES_URL to avoid conflicts with imported Secrets
    """
    # Use PG* variables (Replit native PostgreSQL)
    pg_host = os.getenv("PGHOST")
    pg_db = os.getenv("PGDATABASE")
    pg_user = os.getenv("PGUSER")
    pg_password = os.getenv("PGPASSWORD", "")  # May be empty for local Replit PostgreSQL
    pg_port = os.getenv("PGPORT", "5432")
    
    logger.info(f"PG* variables: PGHOST={pg_host}, PGDATABASE={pg_db}, PGUSER={pg_user}, PGPORT={pg_port}")
    
    if pg_host and pg_db and pg_user:
        # Build URL with or without password
        if pg_password:
            raw_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        else:
            raw_url = f"postgresql://{pg_user}@{pg_host}:{pg_port}/{pg_db}"
        url = _prepare_postgres_url(raw_url)
        logger.info(f"Using PG* variables for PostgreSQL connection ({pg_host}:{pg_port}/{pg_db})")
        return url
    
    logger.error("No valid PostgreSQL configuration found")
    logger.error("Missing required PG* variables: PGHOST, PGDATABASE, or PGUSER")
    logger.error("Current values: PGHOST=%s, PGDATABASE=%s, PGUSER=%s", pg_host, pg_db, pg_user)
    raise ValueError(
        "PostgreSQL not configured. Check .replit file has PGHOST=db, PGDATABASE=replit, PGUSER=replit. "
        "Make sure 'postgresql-16' is in modules list and restart your Repl."
    )

# Lazy initialization - don't create engine at import time
engine = None
SessionLocal = None
Base = declarative_base()

def initialize_database():
    """Initialize database connection - call this at runtime, not import time"""
    global engine, SessionLocal
    
    if engine is not None:
        return engine
    
    try:
        database_url = get_database_url()
        logger.info(f"Connecting to database: {database_url.split('@')[-1] if '@' in database_url else 'database'}")

        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise

# Initialize on first import (but read env vars at runtime)
try:
    initialize_database()
except Exception as e:
    logger.warning(f"Database initialization deferred: {e}")
    # Create dummy sessionmaker for now
    SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
