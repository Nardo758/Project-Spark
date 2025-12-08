from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.opportunity import OpportunityScraperSubmit, Opportunity
from app.models.opportunity import Opportunity as OpportunityModel, OpportunityStatus
from app.models.category import Category
from datetime import datetime

router = APIRouter()

# Simple API key authentication for scrapers
# In production, change this key or move to environment variable
# Generate key: openssl rand -base64 32
SCRAPER_API_KEY = "your-scraper-api-key-change-in-production"


def verify_scraper_api_key(x_api_key: str = Header(...)):
    if x_api_key != SCRAPER_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


@router.post("/opportunities", response_model=Opportunity, status_code=201)
def submit_opportunity(
    opportunity: OpportunityScraperSubmit,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_scraper_api_key)
):
    """
    Endpoint for scrapers to submit discovered opportunities.
    Requires API key authentication via X-API-Key header.
    """
    # Check if opportunity already exists (prevent duplicates)
    if opportunity.source_id:
        existing = db.query(OpportunityModel).filter(
            OpportunityModel.source_id == opportunity.source_id,
            OpportunityModel.source == opportunity.source
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Opportunity already exists")

    # Get category if slug provided
    category_id = None
    if opportunity.category_slug:
        category = db.query(Category).filter(Category.slug == opportunity.category_slug).first()
        if category:
            category_id = category.id

    # Create opportunity
    db_opportunity = OpportunityModel(
        title=opportunity.title,
        description=opportunity.description,
        source=opportunity.source,
        source_url=opportunity.source_url,
        source_id=opportunity.source_id,
        author=opportunity.author,
        author_url=opportunity.author_url,
        category_id=category_id,
        discovered_at=opportunity.discovered_at or datetime.utcnow(),
        status=OpportunityStatus.pending
    )

    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)

    return db_opportunity


@router.post("/opportunities/bulk", response_model=List[Opportunity], status_code=201)
def submit_opportunities_bulk(
    opportunities: List[OpportunityScraperSubmit],
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_scraper_api_key)
):
    """
    Endpoint for scrapers to submit multiple opportunities at once.
    Skips duplicates and returns created opportunities.
    """
    created_opportunities = []

    for opp in opportunities:
        # Check for duplicates
        if opp.source_id:
            existing = db.query(OpportunityModel).filter(
                OpportunityModel.source_id == opp.source_id,
                OpportunityModel.source == opp.source
            ).first()
            if existing:
                continue  # Skip duplicates

        # Get category
        category_id = None
        if opp.category_slug:
            category = db.query(Category).filter(Category.slug == opp.category_slug).first()
            if category:
                category_id = category.id

        # Create opportunity
        db_opportunity = OpportunityModel(
            title=opp.title,
            description=opp.description,
            source=opp.source,
            source_url=opp.source_url,
            source_id=opp.source_id,
            author=opp.author,
            author_url=opp.author_url,
            category_id=category_id,
            discovered_at=opp.discovered_at or datetime.utcnow(),
            status=OpportunityStatus.pending
        )

        db.add(db_opportunity)
        created_opportunities.append(db_opportunity)

    db.commit()

    # Refresh all created opportunities
    for opp in created_opportunities:
        db.refresh(opp)

    return created_opportunities


@router.get("/health")
def scraper_health_check():
    """Health check endpoint for scrapers"""
    return {"status": "healthy", "service": "scraper-api"}
