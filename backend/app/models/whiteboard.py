from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class DrawingType(str, enum.Enum):
    PEN = "pen"
    LINE = "line"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    TEXT = "text"
    STICKY = "sticky"


class Whiteboard(Base):
    __tablename__ = "whiteboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # リレーション
    owner = relationship("User", back_populates="owned_whiteboards")
    drawing_elements = relationship("DrawingElement", back_populates="whiteboard", cascade="all, delete-orphan")
    collaborators = relationship("WhiteboardCollaborator", back_populates="whiteboard", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Whiteboard(id={self.id}, title={self.title}, owner_id={self.owner_id})>"


class DrawingElement(Base):
    __tablename__ = "drawing_elements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    whiteboard_id = Column(UUID(as_uuid=True), ForeignKey("whiteboards.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(DrawingType), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    end_x = Column(Float, nullable=True)
    end_y = Column(Float, nullable=True)
    points = Column(JSON, nullable=True)  # ペンストローク用 [{"x": 10, "y": 20}, ...]
    color = Column(String(7), nullable=False)  # HEX形式 #RRGGBB
    stroke_width = Column(Float, nullable=True)
    fill_color = Column(String(7), nullable=True)  # HEX形式 #RRGGBB
    text_content = Column(Text, nullable=True)
    font_size = Column(Float, nullable=True)
    font_family = Column(String(100), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # リレーション
    whiteboard = relationship("Whiteboard", back_populates="drawing_elements")
    user = relationship("User", back_populates="drawing_elements")
    
    def __repr__(self):
        return f"<DrawingElement(id={self.id}, type={self.type}, whiteboard_id={self.whiteboard_id})>"