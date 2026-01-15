from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
import json

from app.services.upwork_service import UpworkService
from app.db.database import get_db
from app.models.user import User
from app.models.expert_collaboration import ExpertProfile, ExpertCategory
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/upwork", tags=["Upwork Integration"])


@router.get("/search")
async def search_upwork_freelancers(
    q: Optional[str] = Query(None, description="Search query"),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    category: Optional[str] = Query(None, description="Category ID"),
    hourly_rate_min: Optional[float] = Query(None, ge=0),
    hourly_rate_max: Optional[float] = Query(None, le=1000),
    country: Optional[str] = Query(None),
    job_success_min: Optional[int] = Query(None, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Search for freelancers on Upwork.
    Returns external experts that can be displayed in the marketplace.
    """
    skills_list = skills.split(",") if skills else None
    
    result = await UpworkService.search_freelancers(
        query=q,
        skills=skills_list,
        category=category,
        hourly_rate_min=hourly_rate_min,
        hourly_rate_max=hourly_rate_max,
        country=country,
        job_success_min=job_success_min,
        limit=limit,
        offset=offset
    )
    
    return result


@router.get("/categories")
async def get_upwork_categories():
    """Get list of Upwork talent categories."""
    return UpworkService.get_upwork_categories()


@router.get("/profile/{freelancer_id}")
async def get_upwork_profile(
    freelancer_id: str
):
    """Get detailed profile of a specific Upwork freelancer."""
    profile = await UpworkService.get_freelancer_profile(freelancer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Freelancer profile not found")
    return profile


@router.post("/import/{freelancer_id}")
async def import_upwork_freelancer(
    freelancer_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import an Upwork freelancer as an external expert profile.
    Admin only.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    profile_data = await UpworkService.get_freelancer_profile(freelancer_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Freelancer not found on Upwork")
    
    existing = db.query(ExpertProfile).filter(
        ExpertProfile.external_id == freelancer_id,
        ExpertProfile.external_source == "upwork"
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Freelancer already imported")
    
    user_data = profile_data.get("user", {})
    hourly_rate = profile_data.get("hourlyRate", {})
    location = profile_data.get("location", {})
    stats = profile_data.get("stats", {})
    rating = profile_data.get("rating", {})
    skills = profile_data.get("skills", [])
    
    skills_list = [s.get("name", "") for s in skills] if skills else []
    
    expert_profile = ExpertProfile(
        user_id=None,
        title=profile_data.get("title", ""),
        bio=profile_data.get("description", ""),
        hourly_rate_cents=int(hourly_rate.get("amount", 0) * 100) if hourly_rate.get("amount") else None,
        skills=json.dumps(skills_list),
        location=f"{location.get('city', '')}, {location.get('country', '')}".strip(", ") if location else None,
        avatar_url=profile_data.get("portrait", {}).get("portrait") if profile_data.get("portrait") else None,
        avg_rating=rating.get("overallScore") if rating else None,
        total_reviews=0,
        projects_completed=stats.get("totalJobs", 0) if stats else 0,
        is_verified=True,
        is_available=True,
        external_id=freelancer_id,
        external_source="upwork",
        external_url=f"https://www.upwork.com/freelancers/{user_data.get('nid', '')}",
        external_name=user_data.get("name", ""),
        category=ExpertCategory.TECHNICAL_ADVISOR
    )
    
    db.add(expert_profile)
    db.commit()
    db.refresh(expert_profile)
    
    return {
        "id": expert_profile.id,
        "external_id": freelancer_id,
        "name": expert_profile.external_name,
        "title": expert_profile.title,
        "message": "Freelancer imported successfully"
    }


@router.get("/sync")
async def sync_upwork_experts(
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync top Upwork freelancers for a category.
    Updates existing profiles and adds new ones.
    Admin only.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await UpworkService.search_freelancers(
        category=category,
        job_success_min=90,
        limit=limit
    )
    
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
    
    freelancers = result.get("freelancers", [])
    imported = 0
    updated = 0
    
    for f in freelancers:
        existing = db.query(ExpertProfile).filter(
            ExpertProfile.external_id == f["id"],
            ExpertProfile.external_source == "upwork"
        ).first()
        
        if existing:
            existing.title = f.get("title") or existing.title
            if f.get("hourly_rate"):
                existing.hourly_rate_cents = int(f["hourly_rate"] * 100)
            existing.avg_rating = f.get("avg_rating") or existing.avg_rating
            existing.projects_completed = f.get("total_jobs") or existing.projects_completed
            if f.get("skills"):
                existing.skills = json.dumps(f["skills"])
            updated += 1
        else:
            f_skills = f.get("skills", [])
            expert_profile = ExpertProfile(
                user_id=None,
                title=f.get("title", ""),
                bio=f.get("description", ""),
                hourly_rate_cents=int(f["hourly_rate"] * 100) if f.get("hourly_rate") else None,
                skills=json.dumps(f_skills) if f_skills else None,
                location=f"{f.get('city', '')}, {f.get('country', '')}".strip(", ") if f.get("country") else None,
                avatar_url=f.get("avatar_url"),
                avg_rating=f.get("avg_rating"),
                total_reviews=0,
                projects_completed=f.get("total_jobs", 0),
                is_verified=True,
                is_available=True,
                external_id=f["id"],
                external_source="upwork",
                external_url=f.get("profile_url"),
                external_name=f.get("name", ""),
                category=ExpertCategory.TECHNICAL_ADVISOR
            )
            db.add(expert_profile)
            imported += 1
    
    db.commit()
    
    return {
        "total_found": len(freelancers),
        "imported": imported,
        "updated": updated
    }
