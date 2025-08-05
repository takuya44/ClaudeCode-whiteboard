"""
ホワイトボード検索機能のAPIエンドポイント

このモジュールではホワイトボードの高度な検索機能を提供する。
- タグによる検索・絞り込み
- 作成者による検索・絞り込み
- 日付範囲による検索・絞り込み
- 複合検索（複数条件の組み合わせ）
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.search import (
    SearchFiltersSchema,
    SearchResponseSchema,
    TagSchema,
    UserSummarySchema,
)
from app.services.search_service import SearchService

# 検索API用のルーター
router = APIRouter()


@router.post("/whiteboards", response_model=SearchResponseSchema)
def search_whiteboards(
    filters: SearchFiltersSchema,  # 検索フィルター条件
    page: int = 1,                 # ページ番号（デフォルト: 1）
    page_size: int = 10,           # 1ページあたりの件数（デフォルト: 10件）
    db: Session = Depends(get_db), # データベースセッション
    current_user: User = Depends(get_current_active_user)  # 認証済みユーザー
) -> SearchResponseSchema:
    """
    ホワイトボードの高度検索を実行する
    
    検索条件:
    - **tags**: タグIDのリスト（AND条件：すべてのタグを含むホワイトボード）
    - **authors**: 作成者IDのリスト（OR条件：いずれかの作成者によるホワイトボード）
    - **date_range**: 日付範囲フィルター（作成日または更新日の範囲指定）
    - **sort_by**: ソート対象フィールド（created_at, updated_at, title）
    - **sort_order**: ソート方向（asc: 昇順, desc: 降順）
    
    戻り値:
    - 検索結果のホワイトボードリスト（ページネーション付き）
    - 総件数、現在ページ、次ページ有無などの情報
    """
    # 検索サービスのインスタンスを作成
    search_service = SearchService(db)
    
    try:
        # 検索を実行（ユーザーIDを文字列に変換してセキュリティを確保）
        response = search_service.search_whiteboards(
            filters=filters,
            user_id=str(current_user.id),  # UUIDを文字列に変換
            page=page,
            page_size=page_size
        )
        return response
    except ValueError as e:
        # バリデーションエラー（検索条件の不正など）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # その他の予期しないエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching whiteboards"
        )


@router.get("/tags", response_model=List[TagSchema])
def get_available_tags(
    db: Session = Depends(get_db),                       # データベースセッション
    current_user: User = Depends(get_current_active_user) # 認証済みユーザー
) -> List[TagSchema]:
    """
    ユーザーがアクセス可能なタグ一覧を取得する
    
    このエンドポイントは以下のタグを返す:
    - ユーザーが作成したホワイトボードに付与されたタグ
    - ユーザーが閲覧権限を持つホワイトボードに付与されたタグ
    - パブリックなホワイトボードに付与されたタグ
    
    戻り値: タグのリスト（id, name, color, usage_count を含む）
    """
    # 検索サービスのインスタンスを作成
    search_service = SearchService(db)
    
    try:
        # ユーザーがアクセス可能なタグを取得
        tags = search_service.get_available_tags(str(current_user.id))
        return tags
    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching tags"
        )


@router.get("/authors", response_model=List[UserSummarySchema])
def get_available_authors(
    db: Session = Depends(get_db),                       # データベースセッション
    current_user: User = Depends(get_current_active_user) # 認証済みユーザー
) -> List[UserSummarySchema]:
    """
    検索対象となる作成者一覧を取得する
    
    このエンドポイントは以下の作成者を返す:
    - ユーザーがアクセス可能なホワイトボードの作成者
    - パブリックなホワイトボードの作成者
    
    権限による制限:
    - プライベートなホワイトボードの作成者は、アクセス権限がある場合のみ表示
    - 削除されたホワイトボードの作成者は除外
    
    戻り値: ユーザーのリスト（id, name, avatar を含む）
    """
    # 検索サービスのインスタンスを作成
    search_service = SearchService(db)
    
    try:
        # ユーザーがアクセス可能なホワイトボードの作成者を取得
        authors = search_service.get_available_authors(str(current_user.id))
        return authors
    except Exception as e:
        # エラーが発生した場合は500エラーを返す
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching authors"
        )
