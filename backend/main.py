"""Whiteboard API main application module."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
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

