from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
import re

from app.db.database import get_db
from app.core.dependencies import get_current_user_optional
from app.models.user import User
from app.models.opportunity import Opportunity
from app.schemas.opportunity import Opportunity as OpportunitySchema
from app.models.tracking import TrackingEvent
from app.schemas.tracking import TrackingEventCreate

router = APIRouter()


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Simple text similarity calculation using word overlap
    Returns a score between 0 and 1
    """
    # Normalize text
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))

    if not words1 or not words2:
        return 0.0

    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    return intersection / union if union > 0 else 0.0


def calculate_feasibility_score(opportunity: Opportunity) -> float:
    """
    Calculate feasibility score based on multiple factors
    Returns a score between 0 and 100
    """
    score = 0.0

    # Validation count (0-30 points)
    # More validations = more feasible
    validation_score = min(opportunity.validation_count / 10 * 30, 30)
    score += validation_score

    # Severity (0-20 points)
    # Higher severity = more important to solve
    severity_score = (opportunity.severity / 5) * 20
    score += severity_score

    # Growth rate (0-25 points)
    # Positive growth = increasing demand
    growth_score = min(max(opportunity.growth_rate, 0) / 50 * 25, 25)
    score += growth_score

    # Age of problem (0-15 points)
    # Older problems with continued validation = persistent need
    days_old = (datetime.utcnow() - opportunity.created_at.replace(tzinfo=None)).days
    age_score = min(days_old / 365 * 15, 15)
    score += age_score

    # Market size (0-10 points)
    market_score = 0
    if opportunity.market_size:
        if "$500M+" in opportunity.market_size or "$1B+" in opportunity.market_size:
            market_score = 10
        elif "$100M" in opportunity.market_size:
            market_score = 8
        elif "$50M" in opportunity.market_size:
            market_score = 6
        elif "$10M" in opportunity.market_size:
            market_score = 4
    score += market_score

    return round(score, 2)


@router.post("/check-duplicate")
def check_duplicate(
    title: str,
    description: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Check if a similar opportunity already exists
    Returns potential duplicates with similarity scores
    """
    # Get all active opportunities
    opportunities = db.query(Opportunity).filter(
        Opportunity.status == "active"
    ).all()

    potential_duplicates = []

    for opp in opportunities:
        # Calculate title similarity
        title_similarity = calculate_text_similarity(title, opp.title)

        # Calculate description similarity
        desc_similarity = calculate_text_similarity(description, opp.description)

        # Combined score (title weighted more heavily)
        similarity_score = (title_similarity * 0.6) + (desc_similarity * 0.4)

        # If similarity is above threshold, it's a potential duplicate
        if similarity_score > 0.5:  # 50% similarity threshold
            potential_duplicates.append({
                "opportunity_id": opp.id,
                "title": opp.title,
                "similarity_score": round(similarity_score * 100, 2),
                "validation_count": opp.validation_count,
                "created_at": opp.created_at
            })

    # Sort by similarity score
    potential_duplicates.sort(key=lambda x: x['similarity_score'], reverse=True)

    return {
        "is_duplicate": len(potential_duplicates) > 0,
        "duplicate_count": len(potential_duplicates),
        "potential_duplicates": potential_duplicates[:5]  # Return top 5
    }


@router.get("/geographic/by-scope")
def get_opportunities_by_scope(
    scope: str = "online",  # local, regional, national, international, online
    limit: int = 20,
    db: Session = Depends(get_db)
) -> List[OpportunitySchema]:
    """
    Get opportunities filtered by geographic scope
    """
    opportunities = db.query(Opportunity).filter(
        Opportunity.geographic_scope == scope,
        Opportunity.status == "active"
    ).order_by(desc(Opportunity.validation_count)).limit(limit).all()

    return opportunities


@router.get("/geographic/by-location")
def get_opportunities_by_location(
    country: str = None,
    region: str = None,
    city: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> List[OpportunitySchema]:
    """
    Get opportunities filtered by specific location
    """
    query = db.query(Opportunity).filter(Opportunity.status == "active")

    if country:
        query = query.filter(Opportunity.country.ilike(f"%{country}%"))
    if region:
        query = query.filter(Opportunity.region.ilike(f"%{region}%"))
    if city:
        query = query.filter(Opportunity.city.ilike(f"%{city}%"))

    opportunities = query.order_by(desc(Opportunity.validation_count)).limit(limit).all()

    return opportunities


@router.get("/feasibility/{opportunity_id}")
def get_feasibility_analysis(
    opportunity_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed feasibility analysis for an opportunity
    """
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    # Calculate feasibility score
    feasibility_score = calculate_feasibility_score(opportunity)

    # Update the opportunity's feasibility score
    opportunity.feasibility_score = feasibility_score
    db.commit()

    # Determine feasibility level
    if feasibility_score >= 75:
        feasibility_level = "High"
        recommendation = "Highly feasible - Strong market validation and growth"
    elif feasibility_score >= 50:
        feasibility_level = "Medium"
        recommendation = "Moderately feasible - Shows promise but needs more validation"
    elif feasibility_score >= 25:
        feasibility_level = "Low"
        recommendation = "Low feasibility - Limited market validation"
    else:
        feasibility_level = "Very Low"
        recommendation = "Very low feasibility - Insufficient market signals"

    return {
        "opportunity_id": opportunity_id,
        "feasibility_score": feasibility_score,
        "feasibility_level": feasibility_level,
        "recommendation": recommendation,
        "metrics": {
            "validation_count": opportunity.validation_count,
            "severity": opportunity.severity,
            "growth_rate": opportunity.growth_rate,
            "market_size": opportunity.market_size,
            "days_active": (datetime.utcnow() - opportunity.created_at.replace(tzinfo=None)).days
        }
    }


@router.get("/top-feasible")
def get_top_feasible_opportunities(
    limit: int = 10,
    min_score: float = 50.0,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get opportunities with highest feasibility scores
    """
    opportunities = db.query(Opportunity).filter(
        Opportunity.status == "active",
        Opportunity.completion_status == "open"
    ).all()

    # Calculate feasibility for all opportunities
    feasible_opportunities = []
    for opp in opportunities:
        score = calculate_feasibility_score(opp)

        # Update in database
        opp.feasibility_score = score

        if score >= min_score:
            feasible_opportunities.append({
                "id": opp.id,
                "title": opp.title,
                "category": opp.category,
                "feasibility_score": score,
                "validation_count": opp.validation_count,
                "growth_rate": opp.growth_rate,
                "market_size": opp.market_size,
                "geographic_scope": opp.geographic_scope,
                "created_at": opp.created_at
            })

    db.commit()

    # Sort by feasibility score
    feasible_opportunities.sort(key=lambda x: x['feasibility_score'], reverse=True)

    return feasible_opportunities[:limit]


@router.get("/completion-stats")
def get_completion_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get statistics about opportunity completion status
    """
    total = db.query(Opportunity).count()

    open_count = db.query(Opportunity).filter(Opportunity.completion_status == "open").count()
    in_progress = db.query(Opportunity).filter(Opportunity.completion_status == "in_progress").count()
    solved = db.query(Opportunity).filter(Opportunity.completion_status == "solved").count()
    abandoned = db.query(Opportunity).filter(Opportunity.completion_status == "abandoned").count()

    # Recently solved (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recently_solved = db.query(Opportunity).filter(
        Opportunity.completion_status == "solved",
        Opportunity.solved_at >= thirty_days_ago
    ).all()

    return {
        "total_opportunities": total,
        "completion_breakdown": {
            "open": open_count,
            "in_progress": in_progress,
            "solved": solved,
            "abandoned": abandoned
        },
        "completion_rate": round((solved / total * 100) if total > 0 else 0, 2),
        "recently_solved_count": len(recently_solved),
        "recently_solved": [
            {
                "id": opp.id,
                "title": opp.title,
                "solved_by": opp.solved_by,
                "solved_at": opp.solved_at
            }
            for opp in recently_solved
        ]
    }


@router.get("/geographic/distribution")
def get_geographic_distribution(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get distribution of opportunities by geographic scope
    """
    distribution = {}

    for scope in ["local", "regional", "national", "international", "online"]:
        count = db.query(Opportunity).filter(
            Opportunity.geographic_scope == scope,
            Opportunity.status == "active"
        ).count()
        distribution[scope] = count

    # Country distribution
    country_counts = db.query(
        Opportunity.country,
        func.count(Opportunity.id).label('count')
    ).filter(
        Opportunity.country.isnot(None),
        Opportunity.status == "active"
    ).group_by(Opportunity.country).order_by(desc('count')).limit(10).all()

    return {
        "scope_distribution": distribution,
        "top_countries": [
            {"country": country, "count": count}
            for country, count in country_counts
        ]
    }


@router.post("/events", status_code=status.HTTP_201_CREATED)
def track_event(
    payload: TrackingEventCreate,
    request: Request,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Record a lightweight product analytics event.

    Auth is optional; if present we attach user_id.
    """
    # Best-effort request metadata.
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")

    props = payload.properties
    props_json = None
    if props is not None:
        try:
            import json
            props_json = json.dumps(props)
        except Exception:
            props_json = None

    ev = TrackingEvent(
        name=payload.name,
        path=payload.path,
        referrer=payload.referrer,
        user_id=(user.id if user else None),
        anonymous_id=payload.anonymous_id,
        properties=props_json,
        ip_address=ip,
        user_agent=ua,
    )
    db.add(ev)
    db.commit()
    return {"ok": True, "event_id": ev.id}
