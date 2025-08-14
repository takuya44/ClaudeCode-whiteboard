"""Whiteboard API main application module."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.websocket.websocket import websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # startup
    print(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode")
    yield
    # shutdown
    print(f"Shutting down {settings.PROJECT_NAME}")
    _ = app  # 型チェッカーを満足させるための行


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# カスタムバリデーションエラーハンドラー（開発環境専用）
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydanticバリデーションエラーの詳細ログを出力するカスタムハンドラー
    
    開発時のデバッグを効率化するため、422エラーの詳細情報を
    コンソールに出力する。本番環境では詳細ログは出力されない。
    """
    
    # 開発環境でのみ詳細な情報をログ出力
    if settings.ENVIRONMENT == "development":
        print(f"DEBUG: Validation error on {request.method} {request.url}")
        print(f"DEBUG: Validation error details: {exc.errors()}")
        
        # デバッグ用にリクエスト本文を取得を試行
        try:
            body = await request.body()
            print(f"DEBUG: Request body: {body.decode()}")
        except Exception as e:
            print(f"DEBUG: Could not read request body: {e}")
    
    # 標準的な422レスポンスを返す
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation failed"
        }
    )

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """ヘルスチェック用エンドポイント"""
    return {
        "message": "Whiteboard API is running",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

# APIルーターを登録
app.include_router(api_router, prefix=settings.API_V1_STR)

# 簡単なWebSocketテストエンドポイント
@app.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    """WebSocketテストエンドポイント"""
    await websocket.accept()
    await websocket.send_text("Hello WebSocket!")
    await websocket.close()

# WebSocketエンドポイントを登録
@app.websocket("/ws/{whiteboard_id}")
async def websocket_route(
    websocket: WebSocket,
    whiteboard_id: str
):
    """WebSocketエンドポイント"""
    await websocket_endpoint(websocket, whiteboard_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

