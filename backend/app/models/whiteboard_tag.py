"""WhiteboardTag model for many-to-many relationship between whiteboards and tags."""
from typing import Any
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class WhiteboardTag(Base):
    __tablename__ = "whiteboard_tags"
    
    # Composite primary key
    __table_args__ = (
        UniqueConstraint('whiteboard_id', 'tag_id', name='_whiteboard_tag_uc'),
    )

    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    whiteboard_id: Any = Column(UUID(as_uuid=True), ForeignKey("whiteboards.id", ondelete="CASCADE"), nullable=False)
    tag_id: Any = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at: Any = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Any = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # リレーション
    whiteboard = relationship("Whiteboard", back_populates="tags")
    tag = relationship("Tag", back_populates="whiteboard_tags")
    
    def __repr__(self):
        return f"<WhiteboardTag(whiteboard_id={self.whiteboard_id}, tag_id={self.tag_id})>"