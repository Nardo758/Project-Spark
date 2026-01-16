"""
Team Management Models - January 2026

Supports Business Track features:
- Team seats (3/10/unlimited based on tier)
- Team invitations and membership
- Shared opportunity access
- Team branding for white-label reports
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class TeamRole(str, enum.Enum):
    """Team member roles"""
    OWNER = "owner"      # Full access, can manage billing and delete team
    ADMIN = "admin"      # Can manage members and settings
    MEMBER = "member"    # Standard access to team resources


class InviteStatus(str, enum.Enum):
    """Invitation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class Team(Base):
    """A team/organization for Business Track subscribers"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    max_seats = Column(Integer, default=3)  # Based on subscription tier
    
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), nullable=True)  # Hex color for branding
    company_name = Column(String(255), nullable=True)  # For white-label reports
    website_url = Column(String(500), nullable=True)
    
    api_enabled = Column(Boolean, default=False)
    api_rate_limit = Column(Integer, default=100)  # Requests per minute
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    invitations = relationship("TeamInvitation", back_populates="team", cascade="all, delete-orphan")
    api_keys = relationship("TeamApiKey", back_populates="team", cascade="all, delete-orphan")
    
    @property
    def member_count(self) -> int:
        """Current number of active members"""
        return len([m for m in self.members if m.is_active])
    
    @property
    def seats_available(self) -> int:
        """Number of seats available (-1 for unlimited)"""
        if self.max_seats == -1:
            return -1
        return max(0, self.max_seats - self.member_count)
    
    @property
    def has_available_seats(self) -> bool:
        """Check if team has available seats"""
        return self.max_seats == -1 or self.member_count < self.max_seats


class TeamMember(Base):
    """Team membership linking users to teams"""
    __tablename__ = "team_members"
    __table_args__ = (
        UniqueConstraint('team_id', 'user_id', name='uq_team_member'),
    )

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(Enum(TeamRole), default=TeamRole.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True)
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    team = relationship("Team", back_populates="members")
    user = relationship("User")


class TeamInvitation(Base):
    """Invitations to join a team"""
    __tablename__ = "team_invitations"
    __table_args__ = (
        UniqueConstraint('team_id', 'email', 'status', name='uq_team_invitation_pending'),
    )

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    
    email = Column(String(255), nullable=False, index=True)
    role = Column(Enum(TeamRole), default=TeamRole.MEMBER, nullable=False)
    status = Column(Enum(InviteStatus), default=InviteStatus.PENDING, nullable=False)
    
    invite_token = Column(String(255), unique=True, nullable=False, index=True)
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    accepted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="invitations")
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    accepted_by = relationship("User", foreign_keys=[accepted_by_id])


class TeamApiKey(Base):
    """API keys for team API access"""
    __tablename__ = "team_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    key_prefix = Column(String(10), nullable=False)  # First 8 chars for display
    
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0)
    
    scopes = Column(Text, nullable=True)  # JSON array of allowed scopes
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    team = relationship("Team", back_populates="api_keys")
    created_by = relationship("User")
