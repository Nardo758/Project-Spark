from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum as SAEnum
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


class UserWorkspace(Base):
    __tablename__ = "user_workspaces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status = Column(SAEnum(WorkspaceStatus), default=WorkspaceStatus.RESEARCHING, nullable=False)
    progress_percent = Column(Integer, default=0)
    
    custom_title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    ai_context = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="workspaces")
    opportunity = relationship("Opportunity", back_populates="workspaces")
    notes = relationship("WorkspaceNote", back_populates="workspace", cascade="all, delete-orphan")
    tasks = relationship("WorkspaceTask", back_populates="workspace", cascade="all, delete-orphan")
    documents = relationship("WorkspaceDocument", back_populates="workspace", cascade="all, delete-orphan")
    chat_messages = relationship("WorkspaceChatMessage", back_populates="workspace", cascade="all, delete-orphan", order_by="WorkspaceChatMessage.created_at")


class WorkspaceNote(Base):
    __tablename__ = "workspace_notes"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("UserWorkspace", back_populates="notes")


class WorkspaceTask(Base):
    __tablename__ = "workspace_tasks"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    priority = Column(SAEnum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("UserWorkspace", back_populates="tasks")


class WorkspaceDocument(Base):
    __tablename__ = "workspace_documents"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=True)
    content = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("UserWorkspace", back_populates="documents")


class WorkspaceChatMessage(Base):
    __tablename__ = "workspace_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("user_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("UserWorkspace", back_populates="chat_messages")
