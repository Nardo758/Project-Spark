"""
Social Sharing Router

Endpoints for social media sharing and tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.user import User
from app.models.opportunity import Opportunity
from app.core.dependencies import get_current_user
from app.services.social_sharing import social_sharing_service
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()


class ShareRequest(BaseModel):
    """Request to share an opportunity"""
    opportunity_id: int
    platform: str  # 'twitter', 'linkedin', 'facebook', 'email', 'copy_link'


class ShareResponse(BaseModel):
    """Share URL response"""
    url: str
    platform: str
    opportunity_id: int


class ShareStatsResponse(BaseModel):
    """Share statistics response"""
    total_shares: int
    by_platform: dict


@router.post("/share", response_model=ShareResponse)
async def create_share_link(
    share_data: ShareRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Generate a share link for an opportunity and track the share event
    """
    # Validate platform
    valid_platforms = ['twitter', 'linkedin', 'facebook', 'email', 'copy_link']
    if share_data.platform not in valid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        )

    # Get opportunity
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == share_data.opportunity_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    # Generate share URL
    frontend_url = settings.FRONTEND_URL
    share_url = social_sharing_service.generate_share_url(
        opportunity=opportunity,
        platform=share_data.platform,
        base_url=frontend_url
    )

    # Track share event
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    social_sharing_service.track_share(
        db=db,
        opportunity_id=opportunity.id,
        platform=share_data.platform,
        user=current_user,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return {
        "url": share_url,
        "platform": share_data.platform,
        "opportunity_id": opportunity.id
    }


@router.get("/stats/{opportunity_id}", response_model=ShareStatsResponse)
def get_share_stats(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """Get share statistics for an opportunity"""
    # Check if opportunity exists
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    # Get stats
    total_shares = social_sharing_service.get_share_count(db, opportunity_id)
    by_platform = social_sharing_service.get_share_stats(db, opportunity_id)

    return {
        "total_shares": total_shares,
        "by_platform": by_platform
    }


@router.get("/meta-tags/{opportunity_id}")
def get_meta_tags(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """Get Open Graph and Twitter Card meta tags for an opportunity"""
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == opportunity_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    frontend_url = settings.FRONTEND_URL
    meta_tags = social_sharing_service.generate_meta_tags(
        opportunity=opportunity,
        base_url=frontend_url
    )

    return meta_tags


@router.get("/popular")
def get_most_shared_opportunities(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get most shared opportunities"""
    from sqlalchemy import func, desc
    from app.models.share import ShareEvent

    # Query opportunities with share counts
    results = db.query(
        Opportunity.id,
        Opportunity.title,
        Opportunity.category,
        Opportunity.validation_count,
        func.count(ShareEvent.id).label('share_count')
    ).outerjoin(
        ShareEvent,
        Opportunity.id == ShareEvent.opportunity_id
    ).group_by(
        Opportunity.id
    ).order_by(
        desc('share_count')
    ).limit(limit).all()

    return [
        {
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "validation_count": r.validation_count,
            "share_count": r.share_count
        }
        for r in results
    ]
