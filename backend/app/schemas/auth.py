from pydantic import BaseModel, EmailStr


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