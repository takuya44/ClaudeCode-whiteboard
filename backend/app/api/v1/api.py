from fastapi import APIRouter

from app.api.v1 import auth, whiteboards, elements, search

api_router = APIRouter()

# 認証関連
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# ホワイトボード関連
api_router.include_router(
    whiteboards.router,
    prefix="/whiteboards",
    tags=["whiteboards"]
)

# 描画要素関連
api_router.include_router(
    elements.router,
    prefix="/whiteboards",
    tags=["elements"]
)

# 検索関連
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)