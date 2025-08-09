"""
SearchServiceのユニットテスト
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import Mock, MagicMock

from app.services.search_service import SearchService
from app.schemas.search import (
    SearchFiltersSchema,
    DateRangeSchema,
    SearchResponseSchema,
    WhiteboardSearchResultSchema,
    TagSchema,
    UserSummarySchema
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
        """基本的な検索機能のテスト"""
        # Arrange
        user_id = str(uuid4())
        filters = SearchFiltersSchema(
            tags=[],
            authors=[],
            date_range=None,
            sort_by="created_at",
            sort_order="desc"
        )
        
        # モックホワイトボードデータ
        mock_whiteboard = MagicMock()
        mock_whiteboard.id = uuid4()
        mock_whiteboard.title = "Test Whiteboard"
        mock_whiteboard.description = "Test Description"
        mock_whiteboard.created_at = datetime.now()
        mock_whiteboard.updated_at = datetime.now()
        mock_whiteboard.is_public = True
        mock_whiteboard.collaborators = []
        mock_whiteboard.tags = []
        mock_whiteboard.owner.id = uuid4()
        mock_whiteboard.owner.name = "Test User"
        mock_whiteboard.owner.avatar = None
        
        # リポジトリモック
        search_service.repository.find_by_filters = Mock(return_value=([mock_whiteboard], 1))
        
        # Act
        result = search_service.search_whiteboards(filters, user_id, page=1, page_size=10)
        
        # Assert
        assert isinstance(result, SearchResponseSchema)
        assert result.total == 1
        assert len(result.results) == 1
        assert result.page == 1
        assert result.page_size == 10
        assert result.has_next is False
    
    def test_search_whiteboards_with_tags(self, search_service):
        """タグフィルターを使用した検索のテスト"""
        # Arrange
        user_id = str(uuid4())
        tag_id = str(uuid4())
        filters = SearchFiltersSchema(
            tags=[tag_id],
            authors=[],
            date_range=None,
            sort_by="created_at",
            sort_order="desc"
        )
        
        # モックタグ付きホワイトボード
        mock_tag = MagicMock()
        mock_tag.id = uuid4()
        mock_tag.name = "important"
        mock_tag.color = "#FF0000"
        mock_tag.usage_count = 5
        
        mock_whiteboard_tag = MagicMock()
        mock_whiteboard_tag.deleted_at = None
        mock_whiteboard_tag.tag = mock_tag
        
        mock_whiteboard = MagicMock()
        mock_whiteboard.id = uuid4()
        mock_whiteboard.title = "Tagged Whiteboard"
        mock_whiteboard.description = "Has tags"
        mock_whiteboard.created_at = datetime.now()
        mock_whiteboard.updated_at = datetime.now()
        mock_whiteboard.is_public = True
        mock_whiteboard.collaborators = []
        mock_whiteboard.tags = [mock_whiteboard_tag]
        mock_whiteboard.owner.id = uuid4()
        mock_whiteboard.owner.name = "Test User"
        mock_whiteboard.owner.avatar = None
        
        # リポジトリモック
        search_service.repository.find_by_filters = Mock(return_value=([mock_whiteboard], 1))
        
        # Act
        result = search_service.search_whiteboards(filters, user_id)
        
        # Assert
        assert len(result.results) == 1
        assert len(result.results[0].tags) == 1
        assert result.results[0].tags[0].name == "important"
    
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