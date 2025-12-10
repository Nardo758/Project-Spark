from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Add connection arguments for Supabase/PostgreSQL
connect_args = {}
if settings.DATABASE_URL.startswith("postgresql"):
    # Add SSL mode for cloud databases
    connect_args = {"connect_args": {"sslmode": "require"}}

engine = create_engine(
    settings.DATABASE_URL,
    **connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,    # Recycle connections after 5 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
