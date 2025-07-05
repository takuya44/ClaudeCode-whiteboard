from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import User


class WhiteboardBase(BaseModel):
    """ホワイトボード基本スキーマ"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False


class WhiteboardCreate(WhiteboardBase):
    """ホワイトボード作成スキーマ"""


class WhiteboardUpdate(BaseModel):
    """ホワイトボード更新スキーマ"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None


class WhiteboardInDBBase(WhiteboardBase):
    """DB内のホワイトボード基本情報"""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Whiteboard(WhiteboardInDBBase):
    """APIレスポンス用ホワイトボードスキーマ"""
    owner: Optional[User] = None
    collaborators: List[User] = []


class WhiteboardInDB(WhiteboardInDBBase):
    """DB内のホワイトボード完全情報"""


class WhiteboardShare(BaseModel):
    """ホワイトボード共有リクエスト"""
    user_emails: List[str] = Field(..., description="共有するユーザーのメールアドレス一覧")
    permission: str = Field("edit", description="権限レベル (view/edit/admin)")


class WhiteboardPermissionUpdate(BaseModel):
    """ホワイトボード権限更新リクエスト"""
    user_id: UUID
    permission: str = Field(..., description="権限レベル (view/edit/admin)")


class WhiteboardCollaboratorResponse(BaseModel):
    """ホワイトボードコラボレーターレスポンス"""
    user_id: str
    user_name: str
    user_email: str
    permission: str
    joined_at: datetime
    
    class Config:
        from_attributes = True
