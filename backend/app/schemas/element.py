from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class DrawingElementBase(BaseModel):
    """描画要素基本スキーマ（完全に制約なし・デバッグ用）"""
    type: str
    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None
    end_x: Optional[float] = None
    end_y: Optional[float] = None
    points: Optional[List[Dict[str, float]]] = None
    color: str
    stroke_width: Optional[float] = None
    fill_color: Optional[str] = None
    text_content: Optional[str] = None
    font_size: Optional[float] = None
    font_family: Optional[str] = None


class DrawingElementCreate(DrawingElementBase):
    """描画要素作成スキーマ"""
    pass


class DrawingElementUpdate(BaseModel):
    """描画要素更新スキーマ"""
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    end_x: Optional[float] = None
    end_y: Optional[float] = None
    points: Optional[List[Dict[str, float]]] = None
    color: Optional[str] = None
    stroke_width: Optional[int] = None
    fill_color: Optional[str] = None
    text_content: Optional[str] = None
    font_size: Optional[int] = None
    font_family: Optional[str] = None


class DrawingElementInDBBase(DrawingElementBase):
    """DB内の描画要素基本情報"""
    id: UUID
    whiteboard_id: UUID
    user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DrawingElement(DrawingElementInDBBase):
    """APIレスポンス用描画要素スキーマ"""
    pass


class DrawingElementInDB(DrawingElementInDBBase):
    """DB内の描画要素完全情報"""
    pass


class BatchElementsUpdate(BaseModel):
    """バッチ要素更新スキーマ"""
    elements: List[DrawingElementCreate] = Field(..., description="保存する要素配列")