from __future__ import annotations

import enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ConnectionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    BLOCKED = "blocked"


class ThreadType(str, enum.Enum):
    DIRECT = "direct"
    LEAD = "lead"
    OPPORTUNITY = "opportunity"


class ConnectionRequest(Base):
    __tablename__ = "connection_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    status = Column(String(20), nullable=False, default=ConnectionStatus.PENDING.value, index=True)

    context_type = Column(String(40), nullable=True)  # e.g. "lead_purchase", "expert", "profile"
    context_id = Column(String(64), nullable=True)  # string to support multiple resource types
    message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)

    requester = relationship("User", foreign_keys=[requester_id])
    target_user = relationship("User", foreign_keys=[target_user_id])

    __table_args__ = (
        UniqueConstraint("requester_id", "target_user_id", "context_type", "context_id", name="uq_connection_request_pair_context"),
        {"sqlite_autoincrement": True},
    )


class MessageThread(Base):
    __tablename__ = "message_threads"

    id = Column(Integer, primary_key=True, index=True)
    thread_type = Column(String(20), nullable=False, default=ThreadType.DIRECT.value, index=True)

    user_a_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_b_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    context_type = Column(String(40), nullable=True)
    context_id = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    user_a = relationship("User", foreign_keys=[user_a_id])
    user_b = relationship("User", foreign_keys=[user_b_id])
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_a_id", "user_b_id", "context_type", "context_id", name="uq_thread_pair_context"),
        {"sqlite_autoincrement": True},
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("message_threads.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    thread = relationship("MessageThread", back_populates="messages")
    sender = relationship("User")

