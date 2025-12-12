from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)

    # Who is following whom
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], backref="following_relationships")
    following = relationship("User", foreign_keys=[following_id], backref="follower_relationships")

    # Unique constraint - can't follow same user twice
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_follow'),
    )
