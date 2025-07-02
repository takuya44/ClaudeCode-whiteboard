from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "Whiteboard API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "オンラインホワイトボードアプリケーション API"
    
    # API設定
    API_V1_STR: str = "/api/v1"
    
    # セキュリティ設定
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8日間
    
    # データベース設定
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/whiteboard_dev"
    TEST_DATABASE_URL: Optional[str] = None
    
    # CORS設定
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://frontend:3000",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        elif isinstance(v, str):
            return [v]
        raise ValueError(v)
    
    # 環境設定
    ENVIRONMENT: str = "development"
    
    # ログ設定
    LOG_LEVEL: str = "INFO"
    
    # WebSocket設定
    WS_MESSAGE_SIZE_LIMIT: int = 16 * 1024 * 1024  # 16MB
    WS_CONNECTION_LIMIT: int = 1000
    
    # Redis設定（将来的な拡張用）
    REDIS_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_test(self) -> bool:
        return self.ENVIRONMENT == "test"


settings = Settings()