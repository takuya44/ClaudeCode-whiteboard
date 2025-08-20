"""
SearchServiceのユニットテスト

このテストファイルは SearchService クラスの全機能を包括的にテストする:
- 基本検索機能（フィルターなし・各種フィルター）
- バリデーション機能（有効・無効な検索条件）
- エラーハンドリング（無効UUID、例外処理）
- データ変換機能（SQLAlchemy → Pydantic）
- 権限確認（利用可能タグ・作成者取得）
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import Mock, MagicMock

from app.services.search_service import SearchService
from app.schemas.search import (
    SearchFiltersSchema,
    DateRangeSchema,
    SearchResponseSchema,
    WhiteboardSearchResultSchema,
    TagSchema,
    UserSummarySchema,
    ValidationResult
)


class TestSearchService:
    """SearchServiceのテストクラス"""
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return Mock()
    
    @pytest.fixture
    def search_service(self, mock_db):
        """テスト用SearchServiceインスタンス"""
        return SearchService(mock_db)
    
    def test_search_whiteboards_basic(self, search_service, mock_db):
        """基本的な検索機能のテスト
        
        【テストの目的】
        フィルター条件を指定しない基本的な検索が正常に動作することを確認
        
        【テストの流れ】
        1. テスト用の検索条件（フィルターなし）を準備
        2. モックデータ（偽のホワイトボード）を作成
        3. リポジトリの戻り値をモック（実際のDB呼び出しを避ける）
        4. 検索サービスを実行
        5. 返された結果が期待値と一致するかを確認
        """
        # Arrange（準備フェーズ）
        # テスト用のユーザーIDを生成
        user_id = str(uuid4())
        
        # 空の検索フィルターを作成（すべてのホワイトボードを検索）
        filters = SearchFiltersSchema(
            tags=[],           # タグフィルターなし
            authors=[],        # 作成者フィルターなし
            date_range=None,   # 日付範囲フィルターなし
            sort_by="created_at",    # 作成日でソート
            sort_order="desc"        # 降順（新しい順）
        )
        
        # モックホワイトボードデータを作成（実際のDBデータの代わり）
        mock_whiteboard = MagicMock()
        mock_whiteboard.id = uuid4()                          # ユニークID
        mock_whiteboard.title = "Test Whiteboard"            # タイトル
        mock_whiteboard.description = "Test Description"     # 説明
        mock_whiteboard.created_at = datetime.now()          # 作成日時
        mock_whiteboard.updated_at = datetime.now()          # 更新日時
        mock_whiteboard.is_public = True                     # パブリック設定
        mock_whiteboard.collaborators = []                   # コラボレーター一覧（空）
        mock_whiteboard.tags = []                            # タグ一覧（空）
        mock_whiteboard.owner.id = uuid4()                   # 作成者ID
        mock_whiteboard.owner.name = "Test User"             # 作成者名
        mock_whiteboard.owner.avatar = None                  # アバター画像（なし）
        
        # リポジトリの戻り値をモックに設定
        # （実際のデータベースアクセスを避けて、テスト用データを返す）
        search_service.repository.find_by_filters = Mock(
            return_value=([mock_whiteboard], 1)  # (結果リスト, 総件数)
        )
        
        # Act（実行フェーズ）
        # 検索サービスを実際に実行
        result = search_service.search_whiteboards(filters, user_id, page=1, page_size=10)
        
        # Assert（検証フェーズ）
        # 返された結果が期待値と一致するかを確認
        assert isinstance(result, SearchResponseSchema)  # 正しい型で返されているか
        assert result.total == 1                         # 総件数が正しいか
        assert len(result.results) == 1                  # 結果の件数が正しいか
        assert result.page == 1                          # 現在ページが正しいか
        assert result.page_size == 10                    # ページサイズが正しいか
        assert result.has_next is False                  # 次ページの有無が正しいか
    
    def test_search_whiteboards_with_tags(self, search_service):
        """タグフィルターを使用した検索のテスト
        
        【テストの目的】
        特定のタグが付いたホワイトボードを検索する機能のテスト
        
        【テスト内容】
        - タグIDを指定した検索フィルターの動作確認
        - タグ情報が正しく結果に含まれるかの確認
        - ホワイトボード-タグの関連データの正しい変換
        
        【学習ポイント】
        - モックオブジェクトを使った関連データ（タグ）の表現方法
        - 検索結果にタグ情報が適切に含まれることの重要性
        """
        # Arrange（準備フェーズ）
        # テスト用のユーザーIDとタグIDを生成
        user_id = str(uuid4())
        tag_id = str(uuid4())
        
        # タグフィルター付きの検索条件を作成
        filters = SearchFiltersSchema(
            tags=[tag_id],          # 特定のタグで絞り込み
            authors=[],             # 作成者フィルターなし
            date_range=None,        # 日付範囲フィルターなし
            sort_by="created_at",   # 作成日でソート
            sort_order="desc"       # 降順（新しい順）
        )
        
        # モックタグデータを作成（実際のTagモデルの代わり）
        mock_tag = MagicMock()
        mock_tag.id = uuid4()                    # タグのユニークID
        mock_tag.name = "important"             # タグ名
        mock_tag.color = "#FF0000"              # タグの色（赤色）
        mock_tag.usage_count = 5                # タグの使用回数
        
        # ホワイトボード-タグ関連を表すモック（中間テーブル）
        mock_whiteboard_tag = MagicMock()
        mock_whiteboard_tag.deleted_at = None   # 論理削除されていない（アクティブ）
        mock_whiteboard_tag.tag = mock_tag      # 関連するタグ情報
        
        # タグ付きホワイトボードのモックデータを作成
        mock_whiteboard = MagicMock()
        mock_whiteboard.id = uuid4()                              # ホワイトボードID
        mock_whiteboard.title = "Tagged Whiteboard"              # タイトル
        mock_whiteboard.description = "Has tags"                 # 説明
        mock_whiteboard.created_at = datetime.now()              # 作成日時
        mock_whiteboard.updated_at = datetime.now()              # 更新日時
        mock_whiteboard.is_public = True                         # パブリック設定
        mock_whiteboard.collaborators = []                       # コラボレーター一覧
        mock_whiteboard.tags = [mock_whiteboard_tag]             # 関連タグ一覧
        mock_whiteboard.owner.id = uuid4()                       # 作成者ID
        mock_whiteboard.owner.name = "Test User"                 # 作成者名
        mock_whiteboard.owner.avatar = None                      # アバター画像
        
        # リポジトリメソッドの戻り値をモックに設定
        # 実際のデータベース呼び出しの代わりに、テスト用データを返す
        search_service.repository.find_by_filters = Mock(
            return_value=([mock_whiteboard], 1)  # (ホワイトボードリスト, 総件数)
        )
        
        # Act（実行フェーズ）
        # 検索サービスを実行してタグフィルター検索を行う
        result = search_service.search_whiteboards(filters, user_id)
        
        # Assert（検証フェーズ）
        # 検索結果が期待通りかを確認
        assert len(result.results) == 1                    # 1件の結果が返される
        assert len(result.results[0].tags) == 1            # 1つのタグが含まれる
        assert result.results[0].tags[0].name == "important"  # タグ名が正しい
    
    def test_search_whiteboards_with_date_range(self, search_service):
        """日付範囲フィルターを使用した検索のテスト"""
        # Arrange
        user_id = str(uuid4())
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        filters = SearchFiltersSchema(
            tags=[],
            authors=[],
            date_range=DateRangeSchema(
                start=start_date,
                end=end_date,
                type="created"
            ),
            sort_by="created_at",
            sort_order="desc"
        )
        
        # リポジトリモック
        search_service.repository.find_by_filters = Mock(return_value=([], 0))
        
        # Act
        result = search_service.search_whiteboards(filters, user_id)
        
        # Assert
        search_service.repository.find_by_filters.assert_called_once()
        call_args = search_service.repository.find_by_filters.call_args
        assert call_args.kwargs['date_from'] == start_date
        assert call_args.kwargs['date_to'] == end_date
    
    def test_validate_search_filters_valid(self, search_service):
        """有効な検索フィルターのバリデーションテスト"""
        # Arrange
        filters = SearchFiltersSchema(
            tags=[],
            authors=[],
            date_range=None,
            sort_by="created_at",
            sort_order="desc"
        )
        
        # Act
        result = search_service.validate_search_filters(filters)
        
        # Assert
        assert result.is_valid is True
        assert result.errors == {}
    
    
    def test_get_available_tags(self, search_service):
        """利用可能なタグ取得のテスト"""
        # Arrange
        user_id = str(uuid4())
        
        mock_tag = MagicMock()
        mock_tag.id = uuid4()
        mock_tag.name = "project"
        mock_tag.color = "#0000FF"
        mock_tag.usage_count = 10
        
        search_service.repository.get_distinct_tags = Mock(return_value=[mock_tag])
        
        # Act
        result = search_service.get_available_tags(user_id)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], TagSchema)
        assert result[0].name == "project"
    
    def test_get_available_authors(self, search_service):
        """利用可能な作成者取得のテスト"""
        # Arrange
        user_id = str(uuid4())
        
        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.name = "John Doe"
        mock_user.avatar = "https://example.com/avatar.jpg"
        
        search_service.repository.get_distinct_authors = Mock(return_value=[mock_user])
        
        # Act
        result = search_service.get_available_authors(user_id)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], UserSummarySchema)
        assert result[0].name == "John Doe"
    
    # === 追加テスト: バリデーションエラーケース ===
    
    def test_validate_search_filters_invalid_date_range(self, search_service):
        """無効な日付範囲のバリデーションテスト（サービス層でのバリデーション）"""
        # Arrange - Pydanticバリデーションを回避するため、直接DateRangeSchemaを作成
        from pydantic import ValidationError
        
        # Pydanticバリデーションが失敗することを確認
        with pytest.raises(ValidationError):
            end_date = datetime.now() - timedelta(days=1)
            start_date = datetime.now()
            DateRangeSchema(
                start=start_date,
                end=end_date,
                type="created"
            )
        
        # サービス層でのバリデーション用に有効なSchemaを作成してからバリデーション
        # （本来はPydanticで弾かれるが、サービス層のロジックをテストするため）
        filters = SearchFiltersSchema(tags=[], authors=[], date_range=None)
        
        # 手動で無効な日付範囲を設定（テスト用）
        end_date = datetime.now() - timedelta(days=1)
        start_date = datetime.now()
        
        # 無効な状態を直接設定
        if hasattr(filters, 'date_range') and filters.date_range:
            filters.date_range.start = start_date
            filters.date_range.end = end_date
        else:
            # 新しい日付範囲を作成（バリデーションを迂回）
            from unittest.mock import MagicMock
            mock_date_range = MagicMock()
            mock_date_range.start = start_date
            mock_date_range.end = end_date
            filters.date_range = mock_date_range
        
        # Act
        result = search_service.validate_search_filters(filters)
        
        # Assert
        assert result.is_valid is False
        assert "date_range" in result.errors
        assert "Start date must be before end date" in result.errors["date_range"]
    
    def test_validate_search_filters_invalid_sort_field(self, search_service):
        """無効なソートフィールドのバリデーションテスト（サービス層）"""
        # Arrange - Pydantic validation will catch invalid sort fields, so we mock it
        from unittest.mock import MagicMock
        
        # Pydanticバリデーションが失敗することを確認
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            SearchFiltersSchema(
                tags=[],
                authors=[],
                date_range=None,
                sort_by="invalid_field",  # 無効なフィールド
                sort_order="desc"
            )
        
        # サービス層のバリデーションロジックをテストするため、直接操作
        filters = MagicMock()
        filters.date_range = None
        filters.sort_by = "invalid_field"
        filters.sort_order = "desc"
        
        # Act
        result = search_service.validate_search_filters(filters)
        
        # Assert
        assert result.is_valid is False
        assert "sort_by" in result.errors
        assert "Invalid sort field" in result.errors["sort_by"][0]
    
    def test_validate_search_filters_invalid_sort_order(self, search_service):
        """無効なソート順序のバリデーションテスト（サービス層）"""
        # Arrange - Mock the filters to bypass Pydantic validation
        from unittest.mock import MagicMock
        from pydantic import ValidationError
        
        # Pydanticバリデーションが失敗することを確認
        with pytest.raises(ValidationError):
            SearchFiltersSchema(
                tags=[],
                authors=[],
                date_range=None,
                sort_by="created_at",
                sort_order="invalid_order"  # 無効な順序
            )
        
        # サービス層のバリデーションロジックをテストするため、直接操作
        filters = MagicMock()
        filters.date_range = None
        filters.sort_by = "created_at"
        filters.sort_order = "invalid_order"
        
        # Act
        result = search_service.validate_search_filters(filters)
        
        # Assert
        assert result.is_valid is False
        assert "sort_order" in result.errors
        assert "Invalid sort order" in result.errors["sort_order"][0]
    
    # === 追加テスト: エラーハンドリング ===
    
    def test_search_whiteboards_invalid_user_id(self, search_service):
        """無効なユーザーIDでの検索エラーテスト
        
        【テストの目的】
        不正な形式のユーザーIDが入力された場合の適切なエラーハンドリングを確認
        
        【テスト内容】
        - UUID形式ではない文字列をユーザーIDとして渡す
        - ValueError例外が適切に発生することを確認
        - エラーメッセージが適切であることを確認
        
        【学習ポイント】
        - pytest.raises()を使った例外テストの書き方
        - バリデーション処理でのエラーハンドリングの重要性
        - セキュリティ面での入力検証の必要性
        """
        # Arrange（準備フェーズ）
        # 意図的に無効な形式のユーザーIDを準備
        invalid_user_id = "invalid-uuid"  # UUID形式ではない文字列
        
        # 空の検索フィルターを準備（問題はユーザーIDにある）
        filters = SearchFiltersSchema()
        
        # Act & Assert（実行＆検証フェーズ）
        # 無効なユーザーIDでサービスを実行し、例外が発生することを確認
        # pytest.raises()は例外が発生することを期待するテスト構文
        with pytest.raises(ValueError, match="Invalid user ID format"):
            search_service.search_whiteboards(filters, invalid_user_id)
    
    def test_search_whiteboards_invalid_tag_ids(self, search_service):
        """無効なタグIDでの検索エラーテスト"""
        # Arrange
        user_id = str(uuid4())
        filters = SearchFiltersSchema(
            tags=["invalid-tag-uuid"],  # 無効なUUID
            authors=[],
            date_range=None
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid tag ID format"):
            search_service.search_whiteboards(filters, user_id)
    
    def test_search_whiteboards_invalid_author_ids(self, search_service):
        """無効な作成者IDでの検索エラーテスト"""
        # Arrange
        user_id = str(uuid4())
        filters = SearchFiltersSchema(
            tags=[],
            authors=["invalid-author-uuid"],  # 無効なUUID
            date_range=None
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid author ID format"):
            search_service.search_whiteboards(filters, user_id)
    
    def test_search_whiteboards_validation_error(self, search_service):
        """バリデーションエラーのある検索条件でのテスト（サービス層）"""
        # Arrange
        user_id = str(uuid4())
        from unittest.mock import MagicMock
        
        # 無効なフィルターをモック（サービス層でのバリデーションをテストするため）
        filters = MagicMock()
        filters.date_range = MagicMock()
        filters.date_range.start = datetime.now()
        filters.date_range.end = datetime.now() - timedelta(days=1)  # 無効な日付範囲
        filters.sort_by = "created_at"
        filters.sort_order = "desc"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid search filters"):
            search_service.search_whiteboards(filters, user_id)
    
    # === 追加テスト: 複合フィルター ===
    
    def test_search_whiteboards_multiple_filters(self, search_service):
        """複数フィルターを組み合わせた検索のテスト"""
        # Arrange
        user_id = str(uuid4())
        tag_id = str(uuid4())
        author_id = str(uuid4())
        
        filters = SearchFiltersSchema(
            tags=[tag_id],
            authors=[author_id],
            date_range=DateRangeSchema(
                start=datetime.now() - timedelta(days=7),
                end=datetime.now(),
                type="created"
            ),
            sort_by="title",
            sort_order="asc"
        )
        
        # リポジトリモック
        search_service.repository.find_by_filters = Mock(return_value=([], 0))
        
        # Act
        search_service.search_whiteboards(filters, user_id)
        
        # Assert
        search_service.repository.find_by_filters.assert_called_once()
        call_kwargs = search_service.repository.find_by_filters.call_args.kwargs
        assert call_kwargs['tag_ids'] == [UUID(tag_id)]
        assert call_kwargs['author_ids'] == [UUID(author_id)]
        assert call_kwargs['sort_by'] == "title"
        assert call_kwargs['sort_order'] == "asc"
    
    # === 追加テスト: ページネーション ===
    
    def test_search_whiteboards_pagination_first_page(self, search_service):
        """ページネーション: 最初のページのテスト"""
        # Arrange
        user_id = str(uuid4())
        filters = SearchFiltersSchema()
        
        search_service.repository.find_by_filters = Mock(return_value=([], 25))  # 25件の結果
        
        # Act
        result = search_service.search_whiteboards(filters, user_id, page=1, page_size=10)
        
        # Assert
        assert result.page == 1
        assert result.page_size == 10
        assert result.total == 25
        assert result.has_next is True  # 次のページがある
        
        # オフセット計算の確認
        call_kwargs = search_service.repository.find_by_filters.call_args.kwargs
        assert call_kwargs['offset'] == 0
        assert call_kwargs['limit'] == 10
    
    def test_search_whiteboards_pagination_last_page(self, search_service):
        """ページネーション: 最後のページのテスト"""
        # Arrange
        user_id = str(uuid4())
        filters = SearchFiltersSchema()
        
        search_service.repository.find_by_filters = Mock(return_value=([], 23))  # 23件の結果
        
        # Act
        result = search_service.search_whiteboards(filters, user_id, page=3, page_size=10)
        
        # Assert
        assert result.page == 3
        assert result.page_size == 10
        assert result.total == 23
        assert result.has_next is False  # 次のページがない
        
        # オフセット計算の確認（3ページ目なので20件スキップ）
        call_kwargs = search_service.repository.find_by_filters.call_args.kwargs
        assert call_kwargs['offset'] == 20
        assert call_kwargs['limit'] == 10
    
    # === 追加テスト: データ変換 ===
    
    def test_transform_to_search_result_with_tags(self, search_service):
        """タグ付きホワイトボードのデータ変換テスト"""
        # Arrange
        user_id = str(uuid4())
        filters = SearchFiltersSchema()
        
        # タグ付きのモックホワイトボード
        mock_tag = MagicMock()
        mock_tag.id = uuid4()
        mock_tag.name = "important"
        mock_tag.color = "#FF0000"
        mock_tag.usage_count = 5
        
        mock_whiteboard_tag = MagicMock()
        mock_whiteboard_tag.deleted_at = None  # アクティブなタグ
        mock_whiteboard_tag.tag = mock_tag
        
        mock_whiteboard = MagicMock()
        mock_whiteboard.id = uuid4()
        mock_whiteboard.title = "Tagged Board"
        mock_whiteboard.description = "Board with tags"
        mock_whiteboard.created_at = datetime.now()
        mock_whiteboard.updated_at = datetime.now()
        mock_whiteboard.is_public = False
        mock_whiteboard.tags = [mock_whiteboard_tag]
        mock_whiteboard.collaborators = [MagicMock(), MagicMock()]  # 2人のコラボレーター
        mock_whiteboard.owner.id = uuid4()
        mock_whiteboard.owner.name = "Creator User"
        mock_whiteboard.owner.avatar = "https://example.com/avatar.jpg"
        
        search_service.repository.find_by_filters = Mock(return_value=([mock_whiteboard], 1))
        
        # Act
        result = search_service.search_whiteboards(filters, user_id)
        
        # Assert
        search_result = result.results[0]
        assert search_result.collaborator_count == 2
        assert len(search_result.tags) == 1
        assert search_result.tags[0].name == "important"
        assert search_result.tags[0].color == "#FF0000"
        assert search_result.is_public is False
    
    def test_transform_to_search_result_with_deleted_tags(self, search_service):
        """論理削除されたタグを含むホワイトボードのデータ変換テスト"""
        # Arrange
        user_id = str(uuid4())
        filters = SearchFiltersSchema()
        
        # 削除されたタグ
        mock_deleted_tag = MagicMock()
        mock_deleted_tag.deleted_at = datetime.now()  # 削除済み
        
        # アクティブなタグ
        mock_active_tag = MagicMock()
        mock_active_tag.deleted_at = None
        mock_active_tag.tag.id = uuid4()
        mock_active_tag.tag.name = "active"
        mock_active_tag.tag.color = "#00FF00"
        mock_active_tag.tag.usage_count = 3
        
        mock_whiteboard = MagicMock()
        mock_whiteboard.id = uuid4()
        mock_whiteboard.title = "Mixed Tags Board"
        mock_whiteboard.description = "Board with active and deleted tags"
        mock_whiteboard.created_at = datetime.now()
        mock_whiteboard.updated_at = datetime.now()
        mock_whiteboard.is_public = True
        mock_whiteboard.tags = [mock_deleted_tag, mock_active_tag]
        mock_whiteboard.collaborators = []
        mock_whiteboard.owner.id = uuid4()
        mock_whiteboard.owner.name = "Test User"
        mock_whiteboard.owner.avatar = None
        
        search_service.repository.find_by_filters = Mock(return_value=([mock_whiteboard], 1))
        
        # Act
        result = search_service.search_whiteboards(filters, user_id)
        
        # Assert
        search_result = result.results[0]
        assert len(search_result.tags) == 1  # 削除されたタグは除外される
        assert search_result.tags[0].name == "active"
    
    # === 追加テスト: エッジケース ===
    
    def test_search_whiteboards_empty_results(self, search_service):
        """検索結果が0件の場合のテスト"""
        # Arrange
        user_id = str(uuid4())
        filters = SearchFiltersSchema()
        
        search_service.repository.find_by_filters = Mock(return_value=([], 0))
        
        # Act
        result = search_service.search_whiteboards(filters, user_id)
        
        # Assert
        assert len(result.results) == 0
        assert result.total == 0
        assert result.has_next is False
    
    def test_get_available_tags_empty_result(self, search_service):
        """利用可能なタグが0件の場合のテスト"""
        # Arrange
        user_id = str(uuid4())
        search_service.repository.get_distinct_tags = Mock(return_value=[])
        
        # Act
        result = search_service.get_available_tags(user_id)
        
        # Assert
        assert len(result) == 0
        assert isinstance(result, list)
    
    def test_get_available_authors_empty_result(self, search_service):
        """利用可能な作成者が0件の場合のテスト"""
        # Arrange
        user_id = str(uuid4())
        search_service.repository.get_distinct_authors = Mock(return_value=[])
        
        # Act
        result = search_service.get_available_authors(user_id)
        
        # Assert
        assert len(result) == 0
        assert isinstance(result, list)
    
    # === 追加テスト: 複数作成者フィルター ===
    
    def test_search_whiteboards_multiple_authors(self, search_service):
        """複数作成者による検索のテスト（OR検索）"""
        # Arrange
        user_id = str(uuid4())
        author_id_1 = str(uuid4())
        author_id_2 = str(uuid4())
        
        filters = SearchFiltersSchema(
            tags=[],
            authors=[author_id_1, author_id_2],
            date_range=None
        )
        
        search_service.repository.find_by_filters = Mock(return_value=([], 0))
        
        # Act
        search_service.search_whiteboards(filters, user_id)
        
        # Assert
        call_kwargs = search_service.repository.find_by_filters.call_args.kwargs
        expected_author_uuids = [UUID(author_id_1), UUID(author_id_2)]
        assert call_kwargs['author_ids'] == expected_author_uuids
    
    def test_search_whiteboards_multiple_tags(self, search_service):
        """複数タグによる検索のテスト（AND検索）"""
        # Arrange
        user_id = str(uuid4())
        tag_id_1 = str(uuid4())
        tag_id_2 = str(uuid4())
        
        filters = SearchFiltersSchema(
            tags=[tag_id_1, tag_id_2],
            authors=[],
            date_range=None
        )
        
        search_service.repository.find_by_filters = Mock(return_value=([], 0))
        
        # Act
        search_service.search_whiteboards(filters, user_id)
        
        # Assert
        call_kwargs = search_service.repository.find_by_filters.call_args.kwargs
        expected_tag_uuids = [UUID(tag_id_1), UUID(tag_id_2)]
        assert call_kwargs['tag_ids'] == expected_tag_uuids
    
    # === 追加テスト: 複雑なシナリオ ===
    
    def test_search_whiteboards_large_page_size(self, search_service):
        """大きなページサイズでの検索テスト"""
        # Arrange
        user_id = str(uuid4())
        filters = SearchFiltersSchema()
        
        search_service.repository.find_by_filters = Mock(return_value=([], 50))
        
        # Act
        result = search_service.search_whiteboards(filters, user_id, page=1, page_size=100)
        
        # Assert
        assert result.page_size == 100
        assert result.has_next is False  # 50 < 100なので次ページなし
        
        call_kwargs = search_service.repository.find_by_filters.call_args.kwargs
        assert call_kwargs['limit'] == 100
    
    def test_search_whiteboards_updated_date_type(self, search_service):
        """更新日ベースの日付範囲検索テスト"""
        # Arrange
        user_id = str(uuid4())
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        filters = SearchFiltersSchema(
            tags=[],
            authors=[],
            date_range=DateRangeSchema(
                start=start_date,
                end=end_date,
                type="updated"  # 更新日ベース
            )
        )
        
        search_service.repository.find_by_filters = Mock(return_value=([], 0))
        
        # Act
        search_service.search_whiteboards(filters, user_id)
        
        # Assert
        call_kwargs = search_service.repository.find_by_filters.call_args.kwargs
        assert call_kwargs['date_from'] == start_date
        assert call_kwargs['date_to'] == end_date
    
    # === 追加テスト: スキーマバリデーション統合 ===
    
    def test_get_available_tags_with_usage_count(self, search_service):
        """使用回数付きタグ取得のテスト"""
        # Arrange
        user_id = str(uuid4())
        
        mock_tag_high_usage = MagicMock()
        mock_tag_high_usage.id = uuid4()
        mock_tag_high_usage.name = "popular"
        mock_tag_high_usage.color = "#FF0000"
        mock_tag_high_usage.usage_count = 100
        
        mock_tag_low_usage = MagicMock()
        mock_tag_low_usage.id = uuid4()
        mock_tag_low_usage.name = "rare"
        mock_tag_low_usage.color = "#0000FF"
        mock_tag_low_usage.usage_count = 2
        
        search_service.repository.get_distinct_tags = Mock(
            return_value=[mock_tag_high_usage, mock_tag_low_usage]
        )
        
        # Act
        result = search_service.get_available_tags(user_id)
        
        # Assert
        assert len(result) == 2
        assert result[0].usage_count == 100
        assert result[1].usage_count == 2
        assert result[0].name == "popular"
        assert result[1].name == "rare"