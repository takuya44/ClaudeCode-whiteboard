# FastAPI Application Entry Point
# このファイルは実装計画書に従って各担当者が実装してください

from fastapi import FastAPI

app = FastAPI(
    title="Whiteboard API",
    description="オンラインホワイトボードアプリケーション API",
    version="0.1.0"
)

# TODO: 各担当者が以下を実装
# - app/core/config.py (設定)
# - app/core/database.py (DB接続)
# - app/api/routes.py (APIルーター)
# - app/websocket/manager.py (WebSocket管理)

@app.get("/")
async def root():
    """ヘルスチェック用エンドポイント"""
    return {"message": "Whiteboard API is running"}

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)