from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWTトークンレスポンス"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWTトークンペイロード"""
    sub: str | None = None


class Login(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    """パスワード変更リクエスト"""
    current_password: str = Field(..., min_length=8, alias="currentPassword", description="現在のパスワード（8文字以上）")
    new_password: str = Field(..., min_length=8, alias="newPassword", description="新しいパスワード（8文字以上）")