"""
ホワイトボード検索機能のビジネスロジック

このサービスクラスは、ホワイトボードの高度な検索機能を実装する。
主な機能:
- 複合検索（タグ、作成者、日付範囲の組み合わせ）
- 権限ベースのフィルタリング（アクセス制御）
- ページネーション対応
- パフォーマンス最適化（joinedloadによるN+1問題対策）
"""
from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc

from app.models.user import User
from app.models.whiteboard import Whiteboard
from app.models.tag import Tag
from app.models.whiteboard_tag import WhiteboardTag
from app.models.collaborator import WhiteboardCollaborator
from app.schemas.search import (
    SearchFiltersSchema,
    SearchResponseSchema,
    WhiteboardSearchResultSchema,
    TagSchema,
    UserSummarySchema,
    ValidationResult
)


class SearchService:
    """
    ホワイトボード検索サービス
    
    このクラスは、ホワイトボードの検索に関するすべてのビジネスロジックを担当する。
    データベースアクセスとスキーマ変換を組み合わせて、
    APIレイヤーに必要な形式でデータを提供する。
    """
    
    def __init__(self, db: Session):
        """
        検索サービスを初期化する
        
        Args:
            db (Session): SQLAlchemyのデータベースセッション
        """
        self.db = db

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
        2. アクセス権限を考慮したクエリの構築
        3. フィルタリング（タグ、作成者、日付範囲）
        4. ソート処理
        5. ページネーション
        6. 結果の変換とレスポンス構築
        
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

        # 2. アクセス制御とフィルタリングを含むクエリを構築
        query = self._build_search_query(filters, user_id)
        
        # 3. ページネーション前に総件数を取得
        total_count = query.count()
        
        # 4. ソート条件を適用
        query = self._apply_sorting(query, filters.sort_by, filters.sort_order)
        
        # 5. ページネーションを適用
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 6. クエリを実行（joinedloadで関連データも一括取得してN+1問題を回避）
        whiteboards = query.all()
        
        # 7. SQLAlchemyモデルをPydanticスキーマに変換
        search_results = [
            self._transform_to_search_result(wb) for wb in whiteboards
        ]
        
        # 8. レスポンスを構築（次ページの有無も計算）
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
        
        この関数は以下の条件でタグを検索する:
        - ユーザーが作成したホワイトボードのタグ
        - パブリックなホワイトボードのタグ  
        - ユーザーがコラボレーターとして参加しているホワイトボードのタグ
        - 論理削除されていないタグのみ
        
        Args:
            user_id: タグを検索するユーザーのID
            
        Returns:
            List[TagSchema]: アクセス可能なタグのリスト（重複なし、名前順）
        """
        # アクセス可能なホワイトボードのタグを取得するクエリを構築
        query = (
            self.db.query(Tag)
            .distinct()  # 重複を排除
            .join(WhiteboardTag, Tag.id == WhiteboardTag.tag_id)
            .join(Whiteboard, WhiteboardTag.whiteboard_id == Whiteboard.id)
            .outerjoin(WhiteboardCollaborator, Whiteboard.id == WhiteboardCollaborator.whiteboard_id)
            .filter(
                or_(
                    # 自分が作成したホワイトボード
                    Whiteboard.owner_id == user_id,
                    # パブリックなホワイトボード
                    Whiteboard.is_public == True,
                    # コラボレーターとして参加しているホワイトボード
                    WhiteboardCollaborator.user_id == user_id
                )
            )
            .filter(WhiteboardTag.deleted_at.is_(None))  # 論理削除されていないタグのみ
            .order_by(Tag.name)  # タグ名でソート
        )
        
        # クエリを実行
        tags = query.all()
        
        # SQLAlchemyモデルをPydanticスキーマに変換
        tag_schemas = []
        for tag in tags:
            # UUIDを文字列に変換してスキーマを作成
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
        
        この関数は以下の条件でユーザーを検索する:
        - 現在のユーザーがアクセス可能なホワイトボードの作成者
        - パブリックなホワイトボードの作成者
        - コラボレーターとして参加しているホワイトボードの作成者
        
        用途:
        - 検索フィルターの「作成者」選択肢として使用
        - フロントエンドの作成者選択UIに表示
        
        Args:
            user_id: 作成者リストを要求するユーザーのID
            
        Returns:
            List[UserSummarySchema]: アクセス可能な作成者のリスト（重複なし、名前順）
        """
        # アクセス可能なホワイトボードの作成者を取得するクエリを構築
        query = (
            self.db.query(User)
            .distinct()  # 重複する作成者を排除
            .join(Whiteboard, User.id == Whiteboard.owner_id)  # ユーザーとホワイトボードを結合
            .outerjoin(WhiteboardCollaborator, Whiteboard.id == WhiteboardCollaborator.whiteboard_id)
            .filter(
                or_(
                    # 自分が作成したホワイトボード → 自分も作成者リストに含まれる
                    Whiteboard.owner_id == user_id,
                    # パブリックなホワイトボード → 誰でも作成者を見れる
                    Whiteboard.is_public == True,
                    # コラボレーターとして参加 → その作成者を見れる
                    WhiteboardCollaborator.user_id == user_id
                )
            )
            .order_by(User.name)  # ユーザー名でアルファベット順にソート
        )
        
        # クエリを実行
        users = query.all()
        
        # SQLAlchemyモデルをPydanticスキーマに変換
        user_schemas = []
        for user in users:
            # UUIDを文字列に変換してスキーマを作成
            user_data = {
                "id": str(user.id),
                "name": user.name,
                "avatar": user.avatar  # プロフィール画像（オプション）
            }
            user_schemas.append(UserSummarySchema(**user_data))
        return user_schemas

    def validate_search_filters(self, filters: SearchFiltersSchema) -> ValidationResult:
        """
        Validate search filters.
        """
        errors = {}
        
        # Validate date range
        if filters.date_range:
            if filters.date_range.start and filters.date_range.end:
                if filters.date_range.start > filters.date_range.end:
                    errors["date_range"] = ["Start date must be before end date"]
        
        # Validate sort field
        valid_sort_fields = ["created_at", "updated_at", "title"]
        if filters.sort_by not in valid_sort_fields:
            errors["sort_by"] = [f"Invalid sort field. Must be one of: {', '.join(valid_sort_fields)}"]
        
        # Validate sort order
        valid_sort_orders = ["asc", "desc"]
        if filters.sort_order not in valid_sort_orders:
            errors["sort_order"] = [f"Invalid sort order. Must be one of: {', '.join(valid_sort_orders)}"]
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )

    def _build_search_query(self, filters: SearchFiltersSchema, user_id: str):
        """
        検索クエリを構築する（アクセス制御とフィルタリングを含む）
        
        この関数は複雑な検索条件を段階的に構築する:
        1. 基本クエリ（関連テーブルの eager loading 設定）
        2. アクセス制御フィルター（権限チェック）
        3. タグフィルター（AND条件）
        4. 作成者フィルター（OR条件）
        5. 日付範囲フィルター
        
        Args:
            filters: 検索フィルター条件
            user_id: 検索実行ユーザーのID（権限チェック用）
            
        Returns:
            Query: 構築されたSQLAlchemyクエリオブジェクト
        """
        # 1. 基本クエリを構築（N+1問題を避けるためjoinedloadを使用）
        query = (
            self.db.query(Whiteboard)
            .options(
                # 関連データを一括で取得してパフォーマンスを向上
                joinedload(Whiteboard.owner),                        # 作成者情報
                joinedload(Whiteboard.tags).joinedload(WhiteboardTag.tag),  # タグ情報
                joinedload(Whiteboard.collaborators)                 # コラボレーター情報
            )
            .outerjoin(WhiteboardCollaborator, Whiteboard.id == WhiteboardCollaborator.whiteboard_id)
            .distinct()  # 重複を排除
        )
        
        # 2. アクセス制御フィルターを適用（セキュリティ重要）
        access_conditions = [
            # 自分が作成したホワイトボード
            Whiteboard.owner_id == user_id,
            # パブリックなホワイトボード（誰でもアクセス可能）
            Whiteboard.is_public == True,
            # コラボレーターとして参加しているホワイトボード
            WhiteboardCollaborator.user_id == user_id
        ]
        query = query.filter(or_(*access_conditions))
        
        # 3. タグフィルター（AND条件：すべてのタグを含むホワイトボード）
        if filters.tags:
            for tag_id_str in filters.tags:
                # このタグを持つホワイトボードIDを取得するサブクエリ
                tag_whiteboard_ids = (
                    self.db.query(WhiteboardTag.whiteboard_id)
                    .filter(WhiteboardTag.tag_id == tag_id_str)
                    .filter(WhiteboardTag.deleted_at.is_(None))  # 論理削除されていないタグのみ
                    .subquery()
                )
                # メインクエリにサブクエリ結果を適用
                query = query.filter(Whiteboard.id.in_(tag_whiteboard_ids))  # type: ignore
        
        # 4. 作成者フィルター（OR条件：指定された作成者のいずれかが作成）
        if filters.authors:
            query = query.filter(Whiteboard.owner_id.in_(filters.authors))
        
        # 5. 日付範囲フィルター
        if filters.date_range:
            # 作成日または更新日のどちらを対象にするかを決定
            date_field = (
                Whiteboard.created_at if filters.date_range.type == "created"
                else Whiteboard.updated_at
            )
            
            # 開始日フィルター
            if filters.date_range.start:
                query = query.filter(date_field >= filters.date_range.start)
            
            # 終了日フィルター
            if filters.date_range.end:
                query = query.filter(date_field <= filters.date_range.end)
        
        return query

    def _apply_sorting(self, query, sort_by: str, sort_order: str):
        """
        クエリにソート条件を適用する
        
        Args:
            query: ソート対象のSQLAlchemyクエリ
            sort_by: ソート対象フィールド名（created_at, updated_at, title）
            sort_order: ソート方向（asc: 昇順, desc: 降順）
            
        Returns:
            Query: ソート条件が適用されたクエリ
        """
        # ソートフィールド名からSQLAlchemyカラムへのマッピング
        sort_mapping = {
            "created_at": Whiteboard.created_at,    # 作成日時
            "updated_at": Whiteboard.updated_at,    # 更新日時
            "title": Whiteboard.title               # タイトル
        }
        
        # 指定されたフィールドを取得（デフォルトは更新日時）
        sort_field = sort_mapping.get(sort_by, Whiteboard.updated_at)
        
        # ソート方向を適用
        if sort_order == "desc":
            return query.order_by(desc(sort_field))  # 降順（新しい順）
        else:
            return query.order_by(asc(sort_field))   # 昇順（古い順）

    def _transform_to_search_result(self, whiteboard: Whiteboard) -> WhiteboardSearchResultSchema:
        """
        SQLAlchemyのWhiteboardモデルを検索結果用のPydanticスキーマに変換する
        
        このメソッドは以下の処理を行う:
        1. コラボレーター数の計算
        2. 有効なタグ情報の抽出（論理削除されていないタグのみ）
        3. 作成者情報の構築
        4. UUIDの文字列変換
        5. Pydanticスキーマへの変換
        
        Args:
            whiteboard: 変換対象のWhiteboardモデルインスタンス
            
        Returns:
            WhiteboardSearchResultSchema: 検索結果用のスキーマオブジェクト
        """
        # 1. コラボレーター数を計算（権限確認やフィルタリングに使用）
        collaborator_count = len(whiteboard.collaborators)
        
        # 2. 有効なタグ情報を抽出（論理削除されていないタグのみ）
        tags = []
        for wt in whiteboard.tags:
            if wt.deleted_at is None:  # 論理削除チェック
                # UUIDを文字列に変換してPydanticスキーマ用のデータを準備
                tag_data = {
                    "id": str(wt.tag.id),           # UUID → 文字列
                    "name": wt.tag.name,            # タグ名
                    "color": wt.tag.color,          # タグの色（16進数カラーコード）
                    "usage_count": wt.tag.usage_count  # 使用回数
                }
                tags.append(TagSchema(**tag_data))
        
        # 3. 作成者（オーナー）情報を構築
        creator_data = {
            "id": str(whiteboard.owner.id),      # UUID → 文字列
            "name": whiteboard.owner.name,       # ユーザー名
            "avatar": whiteboard.owner.avatar    # プロフィール画像URL（オプション）
        }
        
        # 4. 検索結果データを構築（すべてのUUIDを文字列に変換）
        result_data = {
            "id": str(whiteboard.id),                           # ホワイトボードID
            "title": whiteboard.title,                          # タイトル
            "description": whiteboard.description or "",        # 説明（nullの場合は空文字）
            "creator": UserSummarySchema(**creator_data),       # 作成者情報
            "tags": tags,                                       # タグリスト
            "created_at": whiteboard.created_at,                # 作成日時
            "updated_at": whiteboard.updated_at,                # 更新日時
            "is_public": whiteboard.is_public,                  # パブリック公開フラグ
            "collaborator_count": collaborator_count            # コラボレーター数
        }
        
        # 5. Pydanticスキーマオブジェクトを作成して返す
        return WhiteboardSearchResultSchema(**result_data)