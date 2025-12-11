from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """Get PostgreSQL connection URL dynamically at runtime
    
    Priority:
    1. DATABASE_URL from Replit secrets (preferred)
    2. Construct from PG* environment variables (Replit native PostgreSQL)
    3. POSTGRES_URL secret (only if explicitly set)
    
    Note: Reads environment variables at runtime, not import time
    """
    # First try DATABASE_URL (Replit's standard)
    db_url = os.getenv("DATABASE_URL", "")
    if db_url.startswith(("postgresql://", "postgres://")):
        url = db_url.replace("postgres://", "postgresql://")
        
        # Only add sslmode=require for external databases (not localhost/Replit)
        is_local = "localhost" in url or "127.0.0.1" in url or ".repl.co" in url
        if "sslmode" not in url and not is_local:
            url = url + ("&" if "?" in url else "?") + "sslmode=require"
        
        logger.info(f"Using DATABASE_URL for PostgreSQL connection (SSL: {not is_local})")
        return url
    
    # Try PG* variables (Replit native PostgreSQL)
    pg_host = os.getenv("PGHOST")
    pg_db = os.getenv("PGDATABASE")
    pg_user = os.getenv("PGUSER")
    pg_password = os.getenv("PGPASSWORD")
    pg_port = os.getenv("PGPORT", "5432")
    
    if pg_host and pg_db and pg_user and pg_password:
        # Replit's local PostgreSQL doesn't need SSL
        url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        logger.info(f"Using PG* variables for PostgreSQL connection ({pg_host}:{pg_port}/{pg_db})")
        return url
    
    # Fallback to POSTGRES_URL only if explicitly set
    postgres_url = os.getenv("POSTGRES_URL", "")
    if postgres_url.startswith(("postgresql://", "postgres://")):
        url = postgres_url.replace("postgres://", "postgresql://")
        logger.warning("Using POSTGRES_URL - consider using DATABASE_URL instead")
        return url
    
    logger.error("No valid PostgreSQL URL found. Set DATABASE_URL in Replit Secrets.")
    raise ValueError("Database not configured. Please set DATABASE_URL in Replit Secrets.")

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
