"""
ホワイトボード検索機能のビジネスロジック

このサービスクラスは、ホワイトボードの高度な検索機能を実装する。
主な機能:
- 複合検索（タグ、作成者、日付範囲の組み合わせ）
- 権限ベースのフィルタリング（アクセス制御）
- ページネーション対応
- パフォーマンス最適化（リポジトリパターンによる最適化）
"""
from typing import List
from uuid import UUID

from app.repositories.whiteboard_repository import WhiteboardRepository
from app.schemas.search import (
    SearchFiltersSchema,
    SearchResponseSchema,
    TagSchema,
    UserSummarySchema,
    ValidationResult,
    WhiteboardSearchResultSchema,
)
from sqlalchemy.orm import Session

# 検索設定の定数
VALID_SORT_FIELDS = ["created_at", "updated_at", "title"]
VALID_SORT_ORDERS = ["asc", "desc"]


class SearchService:
    """
    ホワイトボード検索サービス
    
    このクラスは、ホワイトボードの検索に関するすべてのビジネスロジックを担当する。
    リポジトリパターンを使用してデータアクセスを抽象化し、
    APIレイヤーに必要な形式でデータを提供する。
    """
    
    def __init__(self, db: Session):
        """
        検索サービスを初期化する
        
        Args:
            db (Session): SQLAlchemyのデータベースセッション
        """
        self.db = db
        self.repository = WhiteboardRepository(db)

    def search_whiteboards(
        self,
        filters: SearchFiltersSchema,  # 検索フィルター条件
        user_id: str,                  # 検索実行ユーザーのID
        page: int = 1,                 # 取得するページ番号
        page_size: int = 10            # 1ページあたりの件数
    ) -> SearchResponseSchema:
        """
        フィルター条件に基づいてホワイトボードを検索する
        
        この関数は以下の処理を行う:
        1. 検索条件のバリデーション
        2. リポジトリを使用した検索実行
        3. 結果の変換とレスポンス構築
        
        Args:
            filters: 検索フィルター（タグ、作成者、日付範囲、ソート条件）
            user_id: 検索を実行するユーザーのID（権限チェックに使用）
            page: 取得するページ番号（1から開始）
            page_size: 1ページあたりの最大件数
            
        Returns:
            SearchResponseSchema: 検索結果（ホワイトボードリスト、ページネーション情報）
            
        Raises:
            ValueError: 検索条件が無効な場合
        """
        # 1. 検索条件のバリデーションを実行
        validation_result = self.validate_search_filters(filters)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid search filters: {validation_result.errors}")

        # 2. 検索パラメータを準備
        try:
            user_uuid = UUID(user_id)
        except ValueError as e:
            raise ValueError(f"Invalid user ID format: {user_id}") from e
            
        try:
            tag_ids = [UUID(tag_id) for tag_id in filters.tags] if filters.tags else None
        except ValueError as e:
            raise ValueError(f"Invalid tag ID format in: {filters.tags}") from e
            
        try:
            author_ids = [UUID(author_id) for author_id in filters.authors] if filters.authors else None
        except ValueError as e:
            raise ValueError(f"Invalid author ID format in: {filters.authors}") from e
        
        # 日付範囲の処理
        date_from = None
        date_to = None
        if filters.date_range:
            date_from = filters.date_range.start
            date_to = filters.date_range.end
        
        # 3. リポジトリを使用して検索を実行
        offset = (page - 1) * page_size
        whiteboards, total_count = self.repository.find_by_filters(
            user_id=user_uuid,
            tag_ids=tag_ids,
            author_ids=author_ids,
            date_from=date_from,
            date_to=date_to,
            search_text=None,  # テキスト検索は将来実装
            sort_by=filters.sort_by,
            sort_order=filters.sort_order,
            limit=page_size,
            offset=offset
        )
        
        # 4. SQLAlchemyモデルをPydanticスキーマに変換
        search_results = [
            self._transform_to_search_result(wb) for wb in whiteboards
        ]
        
        # 5. レスポンスを構築（次ページの有無も計算）
        return SearchResponseSchema(
            results=search_results,
            total=total_count,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total_count
        )

    def get_available_tags(self, user_id: str) -> List[TagSchema]:
        """
        ユーザーがアクセス可能なホワイトボードのタグ一覧を取得する
        
        Args:
            user_id: タグを検索するユーザーのID
            
        Returns:
            List[TagSchema]: アクセス可能なタグのリスト
        """
        user_uuid = UUID(user_id)
        tags = self.repository.get_distinct_tags(user_uuid)
        
        # SQLAlchemyモデルをPydanticスキーマに変換
        tag_schemas = []
        for tag in tags:
            tag_data = {
                "id": str(tag.id),
                "name": tag.name,
                "color": tag.color,
                "usage_count": tag.usage_count
            }
            tag_schemas.append(TagSchema(**tag_data))
        return tag_schemas

    def get_available_authors(self, user_id: str) -> List[UserSummarySchema]:
        """
        検索対象となる作成者（ユーザー）の一覧を取得する
        
        Args:
            user_id: 作成者リストを要求するユーザーのID
            
        Returns:
            List[UserSummarySchema]: アクセス可能な作成者のリスト
        """
        user_uuid = UUID(user_id)
        users = self.repository.get_distinct_authors(user_uuid)
        
        # SQLAlchemyモデルをPydanticスキーマに変換
        user_schemas = []
        for user in users:
            user_data = {
                "id": str(user.id),
                "name": user.name,
                "avatar": user.avatar
            }
            user_schemas.append(UserSummarySchema(**user_data))
        return user_schemas

    def validate_search_filters(self, filters: SearchFiltersSchema) -> ValidationResult:
        """
        検索フィルターのバリデーション
        
        Args:
            filters: 検索フィルター
            
        Returns:
            ValidationResult: バリデーション結果
        """
        errors = {}
        
        # 日付範囲のバリデーション
        if filters.date_range:
            if filters.date_range.start and filters.date_range.end:
                if filters.date_range.start > filters.date_range.end:
                    errors["date_range"] = ["Start date must be before end date"]
        
        # ソートフィールドのバリデーション
        if filters.sort_by not in VALID_SORT_FIELDS:
            errors["sort_by"] = [f"Invalid sort field. Must be one of: {', '.join(VALID_SORT_FIELDS)}"]
        
        # ソート順序のバリデーション
        if filters.sort_order not in VALID_SORT_ORDERS:
            errors["sort_order"] = [f"Invalid sort order. Must be one of: {', '.join(VALID_SORT_ORDERS)}"]
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )

    def _transform_to_search_result(self, whiteboard) -> WhiteboardSearchResultSchema:
        """
        SQLAlchemyのWhiteboardモデルを検索結果用のPydanticスキーマに変換する
        
        Args:
            whiteboard: 変換対象のWhiteboardモデルインスタンス
            
        Returns:
            WhiteboardSearchResultSchema: 検索結果用のスキーマオブジェクト
        """
        # コラボレーター数を計算
        collaborator_count = len(whiteboard.collaborators)
        
        # 有効なタグ情報を抽出（論理削除されていないタグのみ）
        tags = []
        for wt in whiteboard.tags:
            if wt.deleted_at is None:
                tag_data = {
                    "id": str(wt.tag.id),
                    "name": wt.tag.name,
                    "color": wt.tag.color,
                    "usage_count": wt.tag.usage_count
                }
                tags.append(TagSchema(**tag_data))
        
        # 作成者情報を構築
        creator_data = {
            "id": str(whiteboard.owner.id),
            "name": whiteboard.owner.name,
            "avatar": whiteboard.owner.avatar
        }
        
        # 検索結果データを構築
        result_data = {
            "id": str(whiteboard.id),
            "title": whiteboard.title,
            "description": whiteboard.description or "",
            "creator": UserSummarySchema(**creator_data),
            "tags": tags,
            "created_at": whiteboard.created_at,
            "updated_at": whiteboard.updated_at,
            "is_public": whiteboard.is_public,
            "collaborator_count": collaborator_count
        }
        
        return WhiteboardSearchResultSchema(**result_data)
