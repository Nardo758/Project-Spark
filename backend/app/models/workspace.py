from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class WorkspaceStatus(str, enum.Enum):
    RESEARCHING = "researching"
    VALIDATING = "validating"
    PLANNING = "planning"
    BUILDING = "building"
    LAUNCHED = "launched"
    PAUSED = "paused"
    ARCHIVED = "archived"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


opportunity_tags = Table(
    "opportunity_tags",
    Base.metadata,
    Column("opportunity_id", Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(20), default="#667eea")
    icon = Column(String(50), default="folder")
    is_default = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="collections")
    saved_opportunities = relationship("SavedOpportunity", back_populates="collection", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_user_collection_name"),
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    color = Column(String(20), default="#10b981")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="tags")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_user_tag_name"),
    )


class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    lifecycle_state = Column(String(20), default="saved")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="saved_opportunities")
    opportunity = relationship("Opportunity")
    collection = relationship("Collection", back_populates="saved_opportunities")
    tags = relationship("SavedOpportunityTag", back_populates="saved_opportunity", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "opportunity_id", name="unique_user_saved_opportunity"),
    )


class SavedOpportunityTag(Base):
    __tablename__ = "saved_opportunity_tags"

    id = Column(Integer, primary_key=True, index=True)
    saved_opportunity_id = Column(Integer, ForeignKey("saved_opportunities.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    saved_opportunity = relationship("SavedOpportunity", back_populates="tags")
    tag = relationship("Tag")

    __table_args__ = (
        UniqueConstraint("saved_opportunity_id", "tag_id", name="unique_saved_opp_tag"),
    )


class UserWorkspace(Base):
    __tablename__ = "user_workspaces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    status = Column(SQLEnum("RESEARCHING", "VALIDATING", "PLANNING", "BUILDING", "LAUNCHED", "PAUSED", "ARCHIVED", name="workspacestatus", create_type=False), default="RESEARCHING")
    progress_percent = Column(Integer, default=0)
    custom_title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    ai_context = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="workspaces")
    opportunity = relationship("Opportunity")
    tasks = relationship("WorkspaceTask", back_populates="workspace", cascade="all, delete-orphan")
    notes = relationship("WorkspaceNote", back_populates="workspace", cascade="all, delete-orphan")
    documents = relationship("WorkspaceDocument", back_populates="workspace", cascade="all, delete-orphan")
    chat_messages = relationship("WorkspaceChatMessage", back_populates="workspace", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "opportunity_id", name="unique_user_opportunity_workspace"),
    )


class WorkspaceTask(Base):
    __tablename__ = "workspace_tasks"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    priority = Column(SQLEnum("LOW", "MEDIUM", "HIGH", "URGENT", name="taskpriority", create_type=False), default="MEDIUM")
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("UserWorkspace", back_populates="tasks")


class WorkspaceNote(Base):
    __tablename__ = "workspace_notes"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("UserWorkspace", back_populates="notes")


class WorkspaceDocument(Base):
    __tablename__ = "workspace_documents"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=True)
    content = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("UserWorkspace", back_populates="documents")


class WorkspaceChatMessage(Base):
    __tablename__ = "workspace_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("UserWorkspace", back_populates="chat_messages")
