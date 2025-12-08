from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routes import scraper, auth, opportunities, validations, categories

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Friction API",
    description="Backend API for Friction problem discovery platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scraper.router, prefix="/api/scraper", tags=["Scraper"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(opportunities.router, prefix="/api/opportunities", tags=["Opportunities"])
app.include_router(validations.router, prefix="/api/validations", tags=["Validations"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])


@app.get("/")
def root():
    return {
        "message": "Friction API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
