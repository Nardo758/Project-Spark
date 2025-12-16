from pydantic_settings import BaseSettings
from typing import List, Optional
import json
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "OppGrid API"
    API_V1_PREFIX: str = "/api/v1"

    # Database - Support both DATABASE_URL and REPLIT_DB_URL
    DATABASE_URL: str = ""

    # Supabase (optional - for REST API access)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # URLs - Support Replit environment
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS - allow all origins by default for development
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Email Configuration (Resend)
    RESEND_API_KEY: Optional[str] = None
    FROM_EMAIL: Optional[str] = "noreply@yourdomain.com"

    # OAuth Configuration (Google)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # OAuth Configuration (GitHub)
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # If DATABASE_URL is not set, try REPLIT_DB_URL
        if not self.DATABASE_URL:
            replit_db_url = os.getenv("REPLIT_DB_URL")
            if replit_db_url:
                self.DATABASE_URL = replit_db_url
            else:
                # Fallback for local development
                self.DATABASE_URL = os.getenv(
                    "DATABASE_URL",
                    "postgresql://user:password@localhost:5432/oppgrid_db"
                )

        # Set frontend and backend URLs for Replit environment
        repl_slug = os.getenv("REPL_SLUG")
        repl_owner = os.getenv("REPL_OWNER")
        if repl_slug and repl_owner:
            base_url = f"https://{repl_slug}.{repl_owner}.repl.co"
            if self.BACKEND_URL == "http://localhost:8000":
                self.BACKEND_URL = base_url
            if self.FRONTEND_URL == "http://localhost:3000":
                self.FRONTEND_URL = base_url

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins if they're stored as JSON string"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            try:
                return json.loads(self.BACKEND_CORS_ORIGINS)
            except json.JSONDecodeError:
                return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS


settings = Settings()
