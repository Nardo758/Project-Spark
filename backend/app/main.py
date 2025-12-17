from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, opportunities, validations, comments, users, analytics, watchlist, two_factor, oauth, notifications, admin, moderation, subscriptions, social, follows, websocket_router, ai_chat, webhook, ai_analysis, idea_engine, scraper, replit_auth
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(opportunities.router, prefix=f"{settings.API_V1_PREFIX}/opportunities", tags=["Opportunities"])
app.include_router(validations.router, prefix=f"{settings.API_V1_PREFIX}/validations", tags=["Validations"])
app.include_router(comments.router, prefix=f"{settings.API_V1_PREFIX}/comments", tags=["Comments"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["Analytics"])
app.include_router(watchlist.router, prefix=f"{settings.API_V1_PREFIX}/watchlist", tags=["Watchlist"])
app.include_router(two_factor.router, prefix=f"{settings.API_V1_PREFIX}/2fa", tags=["Two-Factor Auth"])
app.include_router(oauth.router, prefix=f"{settings.API_V1_PREFIX}/oauth", tags=["OAuth"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_PREFIX}/notifications", tags=["Notifications"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(moderation.router, prefix=f"{settings.API_V1_PREFIX}/moderation", tags=["Moderation"])
app.include_router(subscriptions.router, prefix=f"{settings.API_V1_PREFIX}/subscriptions", tags=["Subscriptions"])
app.include_router(social.router, prefix=f"{settings.API_V1_PREFIX}/social", tags=["Social Sharing"])
app.include_router(follows.router, prefix=f"{settings.API_V1_PREFIX}/follows", tags=["Follows"])
app.include_router(websocket_router.router, prefix=f"{settings.API_V1_PREFIX}", tags=["WebSocket"])
app.include_router(ai_chat.router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["AI Chat"])
app.include_router(ai_analysis.router, prefix=f"{settings.API_V1_PREFIX}/ai-analysis", tags=["AI Analysis"])
app.include_router(idea_engine.router, prefix=f"{settings.API_V1_PREFIX}/idea-engine", tags=["Idea Engine"])
app.include_router(webhook.router, prefix=f"{settings.API_V1_PREFIX}", tags=["Webhooks"])
app.include_router(scraper.router, prefix=f"{settings.API_V1_PREFIX}/scraper", tags=["Scraper"])
app.include_router(replit_auth.router, prefix=f"{settings.API_V1_PREFIX}/replit-auth", tags=["Replit Auth"])


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to OppGrid API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        from app.db.database import initialize_database, Base
        logger.info("Initializing database connection...")
        engine = initialize_database()
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("Application starting without database connection. Check DATABASE_URL in Secrets.")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    from app.db.database import SessionLocal
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status
    }
