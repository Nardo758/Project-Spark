from __future__ import annotations

from sqlalchemy import Column, Integer, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from app.db.database import Base


class Brain(Base):
    __tablename__ = "brains"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    name = Column(Text, nullable=False)
    focus_tags = Column(Text, nullable=True)  # JSON array of strings

    match_score = Column(Integer, nullable=False, default=0)  # 0-100
    knowledge_items = Column(Integer, nullable=False, default=0)

    tokens_used = Column(Integer, nullable=False, default=0)
    estimated_cost_usd = Column(Numeric(12, 4), nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="brain")

