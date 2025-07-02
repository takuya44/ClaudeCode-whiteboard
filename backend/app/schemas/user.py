from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserBase(BaseModel):
    """ユーザー基本スキーマ"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    avatar: Optional[str] = None


class UserCreate(UserBase):
    """ユーザー作成スキーマ"""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """ユーザー更新スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserInDBBase(UserBase):
    """DB内のユーザー基本情報"""
    id: UUID
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """APIレスポンス用ユーザースキーマ"""
    pass


class UserInDB(UserInDBBase):
    """DB内のユーザー完全情報（パスワードハッシュ含む）"""
    password_hash: str