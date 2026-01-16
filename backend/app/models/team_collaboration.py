"""
Team Collaboration Models - January 2026

Supports shared access to opportunities within teams
and team activity tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class TeamActivityType(str, enum.Enum):
    """Types of team activity"""
    OPPORTUNITY_SHARED = "opportunity_shared"
    OPPORTUNITY_CLAIMED = "opportunity_claimed"
    REPORT_GENERATED = "report_generated"
    MEMBER_JOINED = "member_joined"
    MEMBER_LEFT = "member_left"
    MEMBER_INVITED = "member_invited"
    COMMENT_ADDED = "comment_added"
    NOTE_ADDED = "note_added"
    WORKSPACE_CREATED = "workspace_created"


class TeamOpportunity(Base):
    """Opportunities shared with a team"""
    __tablename__ = "team_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    shared_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    notes = Column(Text, nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high
    status = Column(String(50), default="new")  # new, reviewing, in_progress, completed, archived
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    team = relationship("Team")
    opportunity = relationship("Opportunity")
    shared_by = relationship("User")


class TeamOpportunityNote(Base):
    """Notes/comments on shared team opportunities"""
    __tablename__ = "team_opportunity_notes"

    id = Column(Integer, primary_key=True, index=True)
    team_opportunity_id = Column(Integer, ForeignKey("team_opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    team_opportunity = relationship("TeamOpportunity")
    user = relationship("User")


class TeamActivity(Base):
    """Activity feed for team actions"""
    __tablename__ = "team_activities"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    
    activity_type = Column(Enum(TeamActivityType), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who performed the action
    
    target_type = Column(String(50), nullable=True)  # opportunity, member, report, etc.
    target_id = Column(Integer, nullable=True)
    target_title = Column(String(255), nullable=True)  # Cached title for display
    
    extra_data = Column(Text, nullable=True)  # JSON for additional context
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team")
    actor = relationship("User")
