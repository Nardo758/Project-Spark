from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """Get PostgreSQL connection URL
    
    Priority:
    1. POSTGRES_URL secret (to bypass .replit override)
    2. DATABASE_URL if it's a valid PostgreSQL URL
    3. Construct from PG* environment variables (Replit native PostgreSQL)
    """
    postgres_url = os.getenv("POSTGRES_URL", "")
    if postgres_url.startswith(("postgresql://", "postgres://")):
        url = postgres_url.replace("postgres://", "postgresql://")
        logger.info("Using POSTGRES_URL for PostgreSQL connection")
        return url
    
    db_url = os.getenv("DATABASE_URL", "")
    if db_url.startswith(("postgresql://", "postgres://")):
        url = db_url.replace("postgres://", "postgresql://")
        if "sslmode" not in url:
            url = url + ("&" if "?" in url else "?") + "sslmode=require"
        logger.info("Using DATABASE_URL for PostgreSQL connection")
        return url
    
    pg_host = os.getenv("PGHOST")
    pg_db = os.getenv("PGDATABASE")
    pg_user = os.getenv("PGUSER")
    pg_password = os.getenv("PGPASSWORD")
    pg_port = os.getenv("PGPORT", "5432")
    
    if pg_host and pg_db and pg_user and pg_password:
        url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}?sslmode=require"
        logger.info(f"Using PG* variables for PostgreSQL connection ({pg_host}:{pg_port}/{pg_db})")
        return url
    
    logger.error("No valid PostgreSQL URL found. Set POSTGRES_URL secret.")
    raise ValueError("Database not configured. Please set POSTGRES_URL secret with your PostgreSQL connection string.")

connect_args = {}

try:
    database_url = get_database_url()
    logger.info(f"Connecting to database: {database_url.split('@')[-1] if '@' in database_url else 'database'}")

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        **connect_args,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    engine = None
    SessionLocal = sessionmaker(autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
