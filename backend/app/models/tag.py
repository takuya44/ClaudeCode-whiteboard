"""Tag model for whiteboard tagging system."""
from typing import Any
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Any = Column(String(100), nullable=False, unique=True, index=True)
    color: Any = Column(String(7), nullable=True)  # Hex color code
    usage_count: Any = Column(Integer, default=0, nullable=False)
    created_at: Any = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Any = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # リレーション
    whiteboard_tags = relationship("WhiteboardTag", back_populates="tag", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"