from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class DrawingElementBase(BaseModel):
    """描画要素基本スキーマ"""
    type: str = Field(..., description="要素タイプ (pen/line/rectangle/circle/text/sticky)")
    x: float = Field(..., description="X座標")
    y: float = Field(..., description="Y座標")
    width: Optional[float] = Field(None, description="幅")
    height: Optional[float] = Field(None, description="高さ")
    end_x: Optional[float] = Field(None, description="終点X座標")
    end_y: Optional[float] = Field(None, description="終点Y座標")
    points: Optional[List[Dict[str, float]]] = Field(None, description="ペンストローク用ポイント配列")
    color: str = Field(..., description="色 (HEX形式)")
    stroke_width: Optional[int] = Field(None, description="線の太さ")
    fill_color: Optional[str] = Field(None, description="塗りつぶし色 (HEX形式)")
    text_content: Optional[str] = Field(None, description="テキスト内容")
    font_size: Optional[int] = Field(None, description="フォントサイズ")
    font_family: Optional[str] = Field(None, description="フォントファミリー")


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