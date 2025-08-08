"""
ホワイトボードデータアクセス層

このリポジトリクラスは、ホワイトボードのデータベースアクセスを担当する。
主な機能:
- 複合条件での検索（タグ、作成者、日付範囲）
- 権限ベースのフィルタリング
- パフォーマンス最適化（インデックス活用、eager loading）
- ページネーションとソート機能
"""
from typing import List, Optional, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.sql import Select

from app.models.whiteboard import Whiteboard
from app.models.whiteboard_tag import WhiteboardTag
from app.models.tag import Tag
from app.models.collaborator import WhiteboardCollaborator
from app.models.user import User


class WhiteboardRepository:
    """
    ホワイトボードリポジトリ
    
    データベースアクセスを抽象化し、ビジネスロジック層（サービス）に
    必要なデータ操作機能を提供する。リポジトリパターンにより、
    データアクセスロジックをビジネスロジックから分離し、
    テスタビリティと保守性を向上させる。
    """
    
    def __init__(self, db: Session):
        """
        リポジトリを初期化する
        
        Args:
            db (Session): SQLAlchemyのデータベースセッション
        """
        self.db = db

    def find_by_filters(
        self,
        user_id: UUID,
        tag_ids: Optional[List[UUID]] = None,
        author_ids: Optional[List[UUID]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search_text: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[Whiteboard], int]:
        """
        複合条件でホワイトボードを検索する
        
        この関数は以下の処理を行う:
        1. 権限チェックを含むベースクエリの構築
        2. 各種フィルター条件の適用（タグ、作成者、日付範囲、テキスト）
        3. 総件数の取得
        4. ソートとページネーション
        5. eager loadingによる関連データの効率的な取得
        
        パフォーマンス最適化:
        - インデックスを活用した高速検索
        - eager loadingによるN+1問題の回避
        - 必要最小限のデータのみを取得
        
        Args:
            user_id: 検索を実行するユーザーのID（権限チェックに使用）
            tag_ids: タグIDのリスト（AND検索：全てのタグを持つホワイトボード）
            author_ids: 作成者IDのリスト（OR検索：いずれかの作成者）
            date_from: 検索期間の開始日
            date_to: 検索期間の終了日
            search_text: テキスト検索文字列（タイトル、説明を対象）
            sort_by: ソート対象フィールド（created_at, updated_at, title）
            sort_order: ソート順序（asc: 昇順, desc: 降順）
            limit: 取得件数の上限（ページネーション用）
            offset: 取得開始位置（ページネーション用）
            
        Returns:
            Tuple[List[Whiteboard], int]: 
                - ホワイトボードのリスト（関連データを含む）
                - 検索条件に一致する総件数
        """
        # 1. ベースクエリの構築（権限チェックを含む）
        query = self._build_base_query(user_id)
        
        # 2. タグフィルターの適用（AND検索：全てのタグを含む）
        if tag_ids:
            query = self._apply_tag_filter(query, tag_ids)
        
        # 3. 作成者フィルターの適用（OR検索：いずれかの作成者）
        if author_ids:
            query = query.filter(Whiteboard.owner_id.in_(author_ids))
        
        # 4. 日付範囲フィルターの適用
        if date_from:
            query = query.filter(Whiteboard.created_at >= date_from)
        if date_to:
            query = query.filter(Whiteboard.created_at <= date_to)
        
        # 5. テキスト検索の適用（部分一致、大文字小文字を区別しない）
        if search_text:
            search_pattern = f"%{search_text}%"
            query = query.filter(
                or_(
                    Whiteboard.title.ilike(search_pattern),      # タイトルの部分一致
                    Whiteboard.description.ilike(search_pattern)  # 説明の部分一致
                )
            )
        
        # 6. 総件数を取得（ページネーション前に実行）
        count_query = select(func.count()).select_from(query.subquery())
        total_count = self.db.execute(count_query).scalar()
        
        # 7. ソート条件を適用
        query = self._apply_sorting(query, sort_by, sort_order)
        
        # 8. ページネーションを適用
        query = query.limit(limit).offset(offset)
        
        # 9. eager loadingで関連データを効率的に取得（N+1問題を回避）
        query = query.options(
            joinedload(Whiteboard.owner),                                    # 作成者情報
            selectinload(Whiteboard.tags).joinedload(WhiteboardTag.tag),    # タグ情報
            selectinload(Whiteboard.collaborators).joinedload(WhiteboardCollaborator.user)  # コラボレーター情報
        )
        
        # 10. クエリを実行して結果を取得
        results = list(self.db.execute(query).unique().scalars().all())
        
        return results, int(total_count or 0)

    def count_by_filters(
        self,
        user_id: UUID,
        tag_ids: Optional[List[UUID]] = None,
        author_ids: Optional[List[UUID]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search_text: Optional[str] = None
    ) -> int:
        """
        フィルター条件に一致するホワイトボードの件数を取得する
        
        find_by_filtersと同じフィルター条件を適用して、
        結果の件数のみを返す。ページネーション計算や
        検索結果の概要表示に使用される。
        
        Args:
            user_id: 検索を実行するユーザーのID
            tag_ids: タグIDのリスト（AND検索）
            author_ids: 作成者IDのリスト（OR検索）
            date_from: 検索期間の開始日
            date_to: 検索期間の終了日
            search_text: テキスト検索文字列
            
        Returns:
            int: 検索条件に一致するホワイトボードの総件数
        """
        query = self._build_base_query(user_id)
        
        if tag_ids:
            query = self._apply_tag_filter(query, tag_ids)
        
        if author_ids:
            query = query.filter(Whiteboard.owner_id.in_(author_ids))
        
        if date_from:
            query = query.filter(Whiteboard.created_at >= date_from)
        if date_to:
            query = query.filter(Whiteboard.created_at <= date_to)
        
        if search_text:
            search_pattern = f"%{search_text}%"
            query = query.filter(
                or_(
                    Whiteboard.title.ilike(search_pattern),
                    Whiteboard.description.ilike(search_pattern)
                )
            )
        
        count_query = select(func.count()).select_from(query.subquery())
        return int(self.db.execute(count_query).scalar() or 0)

    def get_distinct_tags(self, user_id: UUID) -> List[Tag]:
        """
        ユーザーがアクセス可能なホワイトボードで使用されているタグ一覧を取得する
        
        このメソッドは以下の処理を行う:
        1. ユーザーがアクセス可能なホワイトボードを特定
        2. それらのホワイトボードで使用されているタグを抽出
        3. 重複を排除して、使用頻度順にソート
        
        用途:
        - 検索フィルターのタグ選択肢として表示
        - タグの使用状況の把握
        
        Args:
            user_id: タグ一覧を取得するユーザーのID
            
        Returns:
            List[Tag]: アクセス可能なタグのリスト（重複なし、使用頻度順）
        """
        # アクセス可能なホワイトボードのIDを取得
        accessible_whiteboards = self._build_base_query(user_id).subquery()
        
        # それらのホワイトボードで使用されているタグを取得
        query = (
            select(Tag)
            .join(WhiteboardTag, Tag.id == WhiteboardTag.tag_id)
            .join(accessible_whiteboards, WhiteboardTag.whiteboard_id == accessible_whiteboards.c.id)
            .where(WhiteboardTag.deleted_at.is_(None))
            .distinct()
            .order_by(Tag.usage_count.desc(), Tag.name)
        )
        
        return list(self.db.execute(query).scalars().all())

    def get_distinct_authors(self, user_id: UUID) -> List[User]:
        """
        ユーザーがアクセス可能なホワイトボードの作成者一覧を取得する
        
        このメソッドは以下の処理を行う:
        1. ユーザーがアクセス可能なホワイトボードを特定
        2. それらのホワイトボードの作成者を抽出
        3. 重複を排除して、名前順にソート
        
        用途:
        - 検索フィルターの作成者選択肢として表示
        - コラボレーション状況の把握
        
        Args:
            user_id: 作成者一覧を取得するユーザーのID
            
        Returns:
            List[User]: アクセス可能なホワイトボードの作成者リスト（重複なし、名前順）
        """
        # アクセス可能なホワイトボードの作成者を取得
        query = (
            select(User)
            .join(Whiteboard, User.id == Whiteboard.owner_id)
            .join(
                self._build_base_query(user_id).subquery(),
                Whiteboard.id == self._build_base_query(user_id).subquery().c.id
            )
            .distinct()
            .order_by(User.name)
        )
        
        return list(self.db.execute(query).scalars().all())

    def _build_base_query(self, user_id: UUID) -> Select:
        """
        権限チェックを含むベースクエリを構築する（内部メソッド）
        
        アクセス可能なホワイトボードを以下の条件で絞り込む:
        1. 自分が所有者のホワイトボード
        2. パブリックに公開されているホワイトボード
        3. コラボレーターとして参加しているホワイトボード
        
        セキュリティ:
        - ユーザーが閲覧権限を持つホワイトボードのみを返す
        - プライベートなホワイトボードへのアクセスを制限
        
        Args:
            user_id: 権限チェック対象のユーザーID
            
        Returns:
            Select: 権限フィルターが適用されたSQLAlchemyクエリ
        """
        return select(Whiteboard).where(
            or_(
                # 自分が所有者
                Whiteboard.owner_id == user_id,
                # パブリック
                Whiteboard.is_public == True,  # noqa: E712
                # コラボレーター
                Whiteboard.id.in_(
                    select(WhiteboardCollaborator.whiteboard_id)
                    .where(WhiteboardCollaborator.user_id == user_id)
                )
            )
        )

    def _apply_tag_filter(self, query: Select, tag_ids: List[UUID]) -> Select:
        """
        タグフィルター（AND検索）を適用する（内部メソッド）
        
        指定された全てのタグを持つホワイトボードのみを抽出する。
        複数タグが指定された場合、全てのタグを含むホワイトボードのみが
        検索結果に含まれる（AND条件）。
        
        実装詳細:
        - サブクエリを使用して、各タグを持つホワイトボードIDを取得
        - HAVING句で全タグを持つホワイトボードのみを絞り込み
        - 論理削除されたタグは除外
        
        Args:
            query: フィルター適用対象のクエリ
            tag_ids: 検索対象のタグIDリスト
            
        Returns:
            Select: タグフィルターが適用されたクエリ
        """
        # 全ての指定タグを持つホワイトボードのIDを取得
        whiteboard_ids_with_all_tags = (
            select(WhiteboardTag.whiteboard_id)
            .where(
                and_(
                    WhiteboardTag.tag_id.in_(tag_ids),
                    WhiteboardTag.deleted_at.is_(None)
                )
            )
            .group_by(WhiteboardTag.whiteboard_id)
            .having(func.count(WhiteboardTag.tag_id.distinct()) == len(tag_ids))
        )
        
        return query.filter(Whiteboard.id.in_(whiteboard_ids_with_all_tags))

    def _apply_sorting(self, query: Select, sort_by: str, sort_order: str) -> Select:
        """
        ソート条件を適用する（内部メソッド）
        
        指定されたフィールドと順序でクエリにソート条件を追加する。
        インデックスを効率的に活用するため、適切なソート順序を選択する。
        
        サポートするソートフィールド:
        - created_at: 作成日時
        - updated_at: 更新日時
        - title: タイトル（アルファベット順）
        
        Args:
            query: ソート適用対象のクエリ
            sort_by: ソート対象のフィールド名
            sort_order: ソート順序（asc: 昇順, desc: 降順）
            
        Returns:
            Select: ソート条件が適用されたクエリ
        """
        # ソートフィールドのマッピング（デフォルトは作成日時）
        sort_columns = {
            "created_at": Whiteboard.created_at,      # 作成日時
            "updated_at": Whiteboard.updated_at,      # 更新日時
            "title": Whiteboard.title                 # タイトル
        }
        
        # 指定されたフィールドを取得（存在しない場合はデフォルト）
        column = sort_columns.get(sort_by, Whiteboard.created_at)
        
        # ソート順序を適用（インデックスを効率的に活用）
        if sort_order == "asc":
            return query.order_by(asc(column))    # 昇順
        else:
            return query.order_by(desc(column))   # 降順（デフォルト）