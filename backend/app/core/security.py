from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# パスワードハッシュ化設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT設定
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    """
    JWTアクセストークンを作成
    
    Args:
        subject: トークンのsubject（通常はユーザーID）
        expires_delta: 有効期限の差分
    
    Returns:
        エンコードされたJWTトークン
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    平文パスワードとハッシュ化パスワードを検証
    
    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード
    
    Returns:
        パスワードが一致するかどうか
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化
    
    Args:
        password: 平文パスワード
    
    Returns:
        ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)