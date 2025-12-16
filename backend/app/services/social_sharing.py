"""
Social Sharing Service

Generates share URLs and tracks sharing events
"""

from urllib.parse import quote
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.models.share import ShareEvent
from app.models.opportunity import Opportunity
from app.models.user import User


class SocialSharingService:
    """Service for social media sharing"""

    @staticmethod
    def generate_share_url(
        opportunity: Opportunity,
        platform: str,
        base_url: str
    ) -> str:
        """
        Generate platform-specific share URL

        Args:
            opportunity: Opportunity to share
            platform: Social platform ('twitter', 'linkedin', 'facebook', 'email')
            base_url: Frontend base URL

        Returns:
            Share URL for the platform
        """
        # Generate opportunity URL
        opportunity_url = f"{base_url}/opportunities/{opportunity.id}"

        # Generate share text
        title = opportunity.title
        description = opportunity.description[:200] if opportunity.description else ""

        if platform == "twitter":
            text = f"{title}\n\n{description}\n\nShared via OppGrid"
            return f"https://twitter.com/intent/tweet?text={quote(text)}&url={quote(opportunity_url)}"

        elif platform == "linkedin":
            return f"https://www.linkedin.com/sharing/share-offsite/?url={quote(opportunity_url)}"

        elif platform == "facebook":
            return f"https://www.facebook.com/sharer/sharer.php?u={quote(opportunity_url)}"

        elif platform == "email":
            subject = f"Check out this opportunity: {title}"
            body = f"{title}\n\n{description}\n\n{opportunity_url}\n\nShared via OppGrid"
            return f"mailto:?subject={quote(subject)}&body={quote(body)}"

        elif platform == "copy_link":
            return opportunity_url

        else:
            return opportunity_url

    @staticmethod
    def track_share(
        db: Session,
        opportunity_id: int,
        platform: str,
        user: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ShareEvent:
        """
        Track a share event

        Args:
            db: Database session
            opportunity_id: ID of shared opportunity
            platform: Platform where shared
            user: User who shared (optional)
            ip_address: IP address (optional)
            user_agent: User agent (optional)

        Returns:
            Created ShareEvent
        """
        share_event = ShareEvent(
            opportunity_id=opportunity_id,
            user_id=user.id if user else None,
            platform=platform,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(share_event)
        db.commit()
        db.refresh(share_event)

        return share_event

    @staticmethod
    def get_share_count(db: Session, opportunity_id: int) -> int:
        """Get total share count for an opportunity"""
        return db.query(ShareEvent).filter(
            ShareEvent.opportunity_id == opportunity_id
        ).count()

    @staticmethod
    def get_share_stats(db: Session, opportunity_id: int) -> Dict[str, int]:
        """
        Get share statistics by platform

        Args:
            db: Database session
            opportunity_id: Opportunity ID

        Returns:
            Dictionary with platform share counts
        """
        from sqlalchemy import func

        results = db.query(
            ShareEvent.platform,
            func.count(ShareEvent.id).label('count')
        ).filter(
            ShareEvent.opportunity_id == opportunity_id
        ).group_by(ShareEvent.platform).all()

        return {platform: count for platform, count in results}

    @staticmethod
    def generate_meta_tags(opportunity: Opportunity, base_url: str) -> Dict[str, str]:
        """
        Generate Open Graph and Twitter Card meta tags

        Args:
            opportunity: Opportunity to generate tags for
            base_url: Frontend base URL

        Returns:
            Dictionary of meta tags
        """
        opportunity_url = f"{base_url}/opportunities/{opportunity.id}"
        description = opportunity.description[:200] if opportunity.description else "Discover and validate friction points"

        return {
            # Open Graph
            "og:title": opportunity.title,
            "og:description": description,
            "og:url": opportunity_url,
            "og:type": "article",
            "og:site_name": "OppGrid",

            # Twitter Card
            "twitter:card": "summary_large_image",
            "twitter:title": opportunity.title,
            "twitter:description": description,
            "twitter:url": opportunity_url,

            # Additional
            "description": description,
        }


social_sharing_service = SocialSharingService()
