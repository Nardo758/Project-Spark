"""
Badge System for Project-Spark
Defines badge criteria and award logic
"""

from typing import List, Set
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.validation import Validation
from app.models.comment import Comment


class Badge:
    """Badge definition"""
    def __init__(self, id: str, name: str, description: str, icon: str):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon


# Define all available badges
AVAILABLE_BADGES = {
    # Early Adopter Badges
    "early_adopter": Badge(
        id="early_adopter",
        name="Early Adopter",
        description="Joined in the first month",
        icon="🚀"
    ),

    # Validation Badges
    "first_validation": Badge(
        id="first_validation",
        name="First Validation",
        description="Validated your first opportunity",
        icon="👍"
    ),
    "validator_10": Badge(
        id="validator_10",
        name="Validator",
        description="Validated 10 opportunities",
        icon="✋"
    ),
    "validator_50": Badge(
        id="validator_50",
        name="Super Validator",
        description="Validated 50 opportunities",
        icon="⭐"
    ),
    "validator_100": Badge(
        id="validator_100",
        name="Top Validator",
        description="Validated 100+ opportunities",
        icon="🏆"
    ),

    # Sharing Badges
    "first_share": Badge(
        id="first_share",
        name="First Share",
        description="Shared your first opportunity",
        icon="📝"
    ),
    "contributor_5": Badge(
        id="contributor_5",
        name="Contributor",
        description="Shared 5 opportunities",
        icon="📌"
    ),
    "contributor_20": Badge(
        id="contributor_20",
        name="Active Contributor",
        description="Shared 20 opportunities",
        icon="🎯"
    ),

    # Engagement Badges
    "commentator": Badge(
        id="commentator",
        name="Commentator",
        description="Made 10 helpful comments",
        icon="💬"
    ),
    "problem_solver": Badge(
        id="problem_solver",
        name="Problem Solver",
        description="One of your opportunities was marked as solved",
        icon="💡"
    ),

    # Impact Badges
    "impact_100": Badge(
        id="impact_100",
        name="Rising Star",
        description="Earned 100 impact points",
        icon="🌟"
    ),
    "impact_500": Badge(
        id="impact_500",
        name="Influencer",
        description="Earned 500 impact points",
        icon="💫"
    ),
    "impact_1000": Badge(
        id="impact_1000",
        name="Community Leader",
        description="Earned 1000+ impact points",
        icon="👑"
    ),

    # Popularity Badges
    "popular_idea": Badge(
        id="popular_idea",
        name="Viral Idea",
        description="One of your opportunities got 100+ validations",
        icon="🔥"
    ),
    "trending": Badge(
        id="trending",
        name="Trendsetter",
        description="Created an opportunity with high growth rate",
        icon="📈"
    ),
}


class BadgeService:
    """Service to manage badge awards"""

    @staticmethod
    def get_user_badges(user: User) -> List[str]:
        """Get list of badge IDs for a user"""
        if not user.badges:
            return []
        return [badge.strip() for badge in user.badges.split(",") if badge.strip()]

    @staticmethod
    def set_user_badges(user: User, badge_ids: List[str]) -> None:
        """Set badges for a user"""
        user.badges = ",".join(badge_ids) if badge_ids else None

    @staticmethod
    def add_badge(user: User, badge_id: str) -> bool:
        """Add a badge to a user if they don't already have it"""
        if badge_id not in AVAILABLE_BADGES:
            return False

        current_badges = set(BadgeService.get_user_badges(user))

        if badge_id in current_badges:
            return False  # Already has this badge

        current_badges.add(badge_id)
        BadgeService.set_user_badges(user, list(current_badges))
        return True

    @staticmethod
    def check_and_award_badges(user: User, db: Session) -> List[str]:
        """
        Check user's achievements and award appropriate badges
        Returns list of newly awarded badge IDs
        """
        newly_awarded = []

        # Count user's activities
        validation_count = db.query(Validation).filter(Validation.user_id == user.id).count()
        opportunity_count = db.query(Opportunity).filter(Opportunity.author_id == user.id).count()
        comment_count = db.query(Comment).filter(Comment.user_id == user.id).count()

        # Get user's opportunities for additional checks
        user_opportunities = db.query(Opportunity).filter(Opportunity.author_id == user.id).all()

        # Validation badges
        if validation_count >= 1 and BadgeService.add_badge(user, "first_validation"):
            newly_awarded.append("first_validation")

        if validation_count >= 10 and BadgeService.add_badge(user, "validator_10"):
            newly_awarded.append("validator_10")

        if validation_count >= 50 and BadgeService.add_badge(user, "validator_50"):
            newly_awarded.append("validator_50")

        if validation_count >= 100 and BadgeService.add_badge(user, "validator_100"):
            newly_awarded.append("validator_100")

        # Sharing badges
        if opportunity_count >= 1 and BadgeService.add_badge(user, "first_share"):
            newly_awarded.append("first_share")

        if opportunity_count >= 5 and BadgeService.add_badge(user, "contributor_5"):
            newly_awarded.append("contributor_5")

        if opportunity_count >= 20 and BadgeService.add_badge(user, "contributor_20"):
            newly_awarded.append("contributor_20")

        # Comment badge
        if comment_count >= 10 and BadgeService.add_badge(user, "commentator"):
            newly_awarded.append("commentator")

        # Impact badges
        if user.impact_points >= 100 and BadgeService.add_badge(user, "impact_100"):
            newly_awarded.append("impact_100")

        if user.impact_points >= 500 and BadgeService.add_badge(user, "impact_500"):
            newly_awarded.append("impact_500")

        if user.impact_points >= 1000 and BadgeService.add_badge(user, "impact_1000"):
            newly_awarded.append("impact_1000")

        # Opportunity-based badges
        for opp in user_opportunities:
            # Problem solver badge
            if opp.completion_status == "solved" and BadgeService.add_badge(user, "problem_solver"):
                newly_awarded.append("problem_solver")
                break  # Only award once

        for opp in user_opportunities:
            # Popular idea badge
            if opp.validation_count >= 100 and BadgeService.add_badge(user, "popular_idea"):
                newly_awarded.append("popular_idea")
                break  # Only award once

        for opp in user_opportunities:
            # Trending badge
            if opp.growth_rate and opp.growth_rate >= 20 and BadgeService.add_badge(user, "trending"):
                newly_awarded.append("trending")
                break  # Only award once

        return newly_awarded

    @staticmethod
    def get_badge_info(badge_id: str) -> dict:
        """Get badge information"""
        badge = AVAILABLE_BADGES.get(badge_id)
        if not badge:
            return None

        return {
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon
        }

    @staticmethod
    def get_all_badges() -> List[dict]:
        """Get all available badges"""
        return [
            {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon
            }
            for badge in AVAILABLE_BADGES.values()
        ]


def award_impact_points(user: User, points: int, db: Session) -> None:
    """Award impact points to a user and check for new badges"""
    user.impact_points += points
    BadgeService.check_and_award_badges(user, db)
    db.commit()
