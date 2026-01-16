"""
Team Collaboration Service - January 2026

Handles shared opportunity access and team activity tracking.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.team import Team, TeamMember, TeamRole
from app.models.team_collaboration import TeamOpportunity, TeamOpportunityNote, TeamActivity, TeamActivityType
from app.models.opportunity import Opportunity
from app.models.user import User

logger = logging.getLogger(__name__)


def share_opportunity_with_team(
    team_id: int,
    opportunity_id: int,
    user: User,
    notes: Optional[str] = None,
    priority: str = "medium",
    db: Session = None
) -> Tuple[bool, str, Optional[TeamOpportunity]]:
    """
    Share an opportunity with a team.
    """
    # Check if user is a member of the team
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not member:
        return False, "You are not a member of this team", None
    
    # Check if opportunity exists
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        return False, "Opportunity not found", None
    
    # Check if already shared
    existing = db.query(TeamOpportunity).filter(
        TeamOpportunity.team_id == team_id,
        TeamOpportunity.opportunity_id == opportunity_id
    ).first()
    
    if existing:
        return False, "This opportunity is already shared with the team", None
    
    # Create the shared opportunity
    team_opp = TeamOpportunity(
        team_id=team_id,
        opportunity_id=opportunity_id,
        shared_by_id=user.id,
        notes=notes,
        priority=priority
    )
    db.add(team_opp)
    
    # Log activity
    log_team_activity(
        team_id=team_id,
        activity_type=TeamActivityType.OPPORTUNITY_SHARED,
        actor_id=user.id,
        target_type="opportunity",
        target_id=opportunity_id,
        target_title=opportunity.title,
        db=db
    )
    
    db.commit()
    db.refresh(team_opp)
    
    return True, "Opportunity shared with team", team_opp


def get_team_opportunities(
    team_id: int,
    user: User,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    db: Session = None
) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    Get all opportunities shared with a team.
    """
    # Check membership
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not member:
        return False, "You are not a member of this team", []
    
    query = db.query(TeamOpportunity).filter(TeamOpportunity.team_id == team_id)
    
    if status_filter:
        query = query.filter(TeamOpportunity.status == status_filter)
    if priority_filter:
        query = query.filter(TeamOpportunity.priority == priority_filter)
    
    team_opps = query.order_by(TeamOpportunity.created_at.desc()).all()
    
    result = []
    for to in team_opps:
        opp = to.opportunity
        result.append({
            "id": to.id,
            "opportunity_id": opp.id,
            "title": opp.title,
            "category": opp.category,
            "city": opp.city,
            "region": opp.region,
            "ai_opportunity_score": opp.ai_opportunity_score,
            "notes": to.notes,
            "priority": to.priority,
            "status": to.status,
            "shared_by": to.shared_by.name if to.shared_by else "Unknown",
            "shared_by_id": to.shared_by_id,
            "created_at": to.created_at.isoformat() if to.created_at else None,
        })
    
    return True, "Success", result


def update_team_opportunity_status(
    team_opportunity_id: int,
    user: User,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = None
) -> Tuple[bool, str]:
    """
    Update a team opportunity's status or priority.
    Only admin/owner or the person who shared it can update.
    """
    team_opp = db.query(TeamOpportunity).filter(TeamOpportunity.id == team_opportunity_id).first()
    if not team_opp:
        return False, "Team opportunity not found"
    
    # Check membership
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_opp.team_id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not member:
        return False, "You are not a member of this team"
    
    # Permission check: only sharer, admin, or owner can update status/priority
    can_update_status = (
        team_opp.shared_by_id == user.id or 
        member.role in [TeamRole.OWNER, TeamRole.ADMIN]
    )
    
    if (status or priority) and not can_update_status:
        return False, "Only the person who shared this or admins can update status/priority"
    
    if status:
        team_opp.status = status
    if priority:
        team_opp.priority = priority
    if notes is not None:
        team_opp.notes = notes
    
    db.commit()
    return True, "Updated successfully"


def add_opportunity_note(
    team_opportunity_id: int,
    user: User,
    content: str,
    db: Session = None
) -> Tuple[bool, str, Optional[TeamOpportunityNote]]:
    """
    Add a note to a team opportunity.
    """
    team_opp = db.query(TeamOpportunity).filter(TeamOpportunity.id == team_opportunity_id).first()
    if not team_opp:
        return False, "Team opportunity not found", None
    
    # Check membership
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_opp.team_id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not member:
        return False, "You are not a member of this team", None
    
    note = TeamOpportunityNote(
        team_opportunity_id=team_opportunity_id,
        user_id=user.id,
        content=content
    )
    db.add(note)
    
    # Log activity
    log_team_activity(
        team_id=team_opp.team_id,
        activity_type=TeamActivityType.NOTE_ADDED,
        actor_id=user.id,
        target_type="team_opportunity",
        target_id=team_opportunity_id,
        target_title=team_opp.opportunity.title if team_opp.opportunity else None,
        db=db
    )
    
    db.commit()
    db.refresh(note)
    
    return True, "Note added", note


def get_opportunity_notes(
    team_opportunity_id: int,
    user: User,
    db: Session = None
) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    Get all notes for a team opportunity.
    """
    team_opp = db.query(TeamOpportunity).filter(TeamOpportunity.id == team_opportunity_id).first()
    if not team_opp:
        return False, "Team opportunity not found", []
    
    # Check membership
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_opp.team_id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not member:
        return False, "You are not a member of this team", []
    
    notes = db.query(TeamOpportunityNote).filter(
        TeamOpportunityNote.team_opportunity_id == team_opportunity_id
    ).order_by(TeamOpportunityNote.created_at.desc()).all()
    
    return True, "Success", [
        {
            "id": n.id,
            "content": n.content,
            "user_id": n.user_id,
            "user_name": n.user.name if n.user else "Unknown",
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notes
    ]


def log_team_activity(
    team_id: int,
    activity_type: TeamActivityType,
    actor_id: int,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    target_title: Optional[str] = None,
    metadata: Optional[Dict] = None,
    db: Session = None
) -> TeamActivity:
    """
    Log an activity to the team feed.
    """
    activity = TeamActivity(
        team_id=team_id,
        activity_type=activity_type,
        actor_id=actor_id,
        target_type=target_type,
        target_id=target_id,
        target_title=target_title,
        extra_data=json.dumps(metadata) if metadata else None
    )
    db.add(activity)
    # Don't commit here - let caller handle transaction
    return activity


def get_team_activity_feed(
    team_id: int,
    user: User,
    limit: int = 50,
    offset: int = 0,
    db: Session = None
) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    Get the activity feed for a team.
    """
    # Check membership
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not member:
        return False, "You are not a member of this team", []
    
    activities = db.query(TeamActivity).filter(
        TeamActivity.team_id == team_id
    ).order_by(TeamActivity.created_at.desc()).offset(offset).limit(limit).all()
    
    return True, "Success", [
        {
            "id": a.id,
            "activity_type": a.activity_type.value,
            "actor_id": a.actor_id,
            "actor_name": a.actor.name if a.actor else "Unknown",
            "target_type": a.target_type,
            "target_id": a.target_id,
            "target_title": a.target_title,
            "extra_data": json.loads(a.extra_data) if a.extra_data else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in activities
    ]


def remove_shared_opportunity(
    team_opportunity_id: int,
    user: User,
    db: Session = None
) -> Tuple[bool, str]:
    """
    Remove a shared opportunity from the team.
    Only the person who shared it or admins/owners can remove.
    """
    team_opp = db.query(TeamOpportunity).filter(TeamOpportunity.id == team_opportunity_id).first()
    if not team_opp:
        return False, "Team opportunity not found"
    
    # Check membership and permissions
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_opp.team_id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not member:
        return False, "You are not a member of this team"
    
    # Only sharer or admin/owner can remove
    if team_opp.shared_by_id != user.id and member.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
        return False, "You don't have permission to remove this opportunity"
    
    db.delete(team_opp)
    db.commit()
    
    return True, "Opportunity removed from team"
