from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ContentType(str, enum.Enum):
    """Types of content that can be reported"""
    OPPORTUNITY = "opportunity"
    COMMENT = "comment"
    USER = "user"


class ReportReason(str, enum.Enum):
    """Reasons for reporting content"""
    SPAM = "spam"
    HARASSMENT = "harassment"
    INAPPROPRIATE = "inappropriate"
    DUPLICATE = "duplicate"
    MISLEADING = "misleading"
    OFF_TOPIC = "off_topic"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    """Status of a moderation report"""
    PENDING = "pending"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    # Reporter information
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Reported content
    content_type = Column(Enum(ContentType), nullable=False)
    content_id = Column(Integer, nullable=False)  # ID of the reported item

    # Report details
    reason = Column(Enum(ReportReason), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)

    # Moderation action
    moderator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    moderator_notes = Column(Text, nullable=True)
    action_taken = Column(String(50), nullable=True)  # 'deleted', 'warned', 'dismissed', etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id])
    moderator = relationship("User", foreign_keys=[moderator_id])


class ModerationLog(Base):
    __tablename__ = "moderation_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Moderator
    moderator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Action details
    action = Column(String(50), nullable=False)  # 'delete_opportunity', 'ban_user', 'approve_content', etc.
    content_type = Column(String(50), nullable=False)
    content_id = Column(Integer, nullable=False)

    # Context
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    moderator = relationship("User", foreign_keys=[moderator_id])
