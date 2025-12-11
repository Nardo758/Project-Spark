from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """Get PostgreSQL connection URL
    
    Uses POSTGRES_URL secret (to bypass .replit override) or DATABASE_URL if valid.
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
