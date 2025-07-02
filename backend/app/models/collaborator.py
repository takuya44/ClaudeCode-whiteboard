from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class Permission(str, enum.Enum):
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin"


class WhiteboardCollaborator(Base):
    __tablename__ = "whiteboard_collaborators"
    __table_args__ = (
        UniqueConstraint('whiteboard_id', 'user_id', name='_whiteboard_user_uc'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    whiteboard_id = Column(UUID(as_uuid=True), ForeignKey("whiteboards.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission = Column(Enum(Permission), default=Permission.EDIT, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # リレーション
    whiteboard = relationship("Whiteboard", back_populates="collaborators")
    user = relationship("User", back_populates="collaborations")
    
    def __repr__(self):
        return f"<WhiteboardCollaborator(id={self.id}, whiteboard_id={self.whiteboard_id}, user_id={self.user_id}, permission={self.permission})>"