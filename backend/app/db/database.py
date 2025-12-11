from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """Construct PostgreSQL URL from environment variables
    
    Priority order:
    1. DATABASE_URL if it starts with postgresql:// or postgres://
    2. Build URL from PG* env vars if PGHOST is not localhost
    3. Fallback to localhost (will fail if no local postgres)
    """
    db_url = os.getenv("DATABASE_URL", "")
    
    if db_url and (db_url.startswith("postgresql://") or db_url.startswith("postgres://")):
        url = db_url.replace("postgres://", "postgresql://")
        if "sslmode" not in url:
            url = url + ("&" if "?" in url else "?") + "sslmode=require"
        logger.info(f"Using DATABASE_URL for PostgreSQL connection")
        return url
    
    pg_host = os.getenv("PGHOST", "")
    pg_port = os.getenv("PGPORT", "5432")
    pg_user = os.getenv("PGUSER", "")
    pg_password = os.getenv("PGPASSWORD", "")
    pg_database = os.getenv("PGDATABASE", "")
    
    if all([pg_host, pg_user, pg_password, pg_database]) and pg_host not in ["localhost", "127.0.0.1", "::1"]:
        url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}?sslmode=require"
        logger.info(f"Using PostgreSQL connection from PG* env vars: {pg_host}")
        return url
    
    logger.warning(f"No valid PostgreSQL configuration found. DATABASE_URL={db_url[:50] if db_url else 'empty'}... PGHOST={pg_host}")
    return "postgresql://user:password@localhost:5432/friction_db"

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
