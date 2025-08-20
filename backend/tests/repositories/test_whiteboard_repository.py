"""
WhiteboardRepositoryのユニットテスト

このテストファイルは WhiteboardRepository クラスの全機能を包括的にテストする:
- 複合検索クエリ（タグ、作成者、日付範囲フィルター）
- 権限ベースのフィルタリング（アクセス制御）
- ページネーション・ソート機能
- データベース統合機能（実際のSQLクエリ実行）
- タグ・作成者一覧取得機能
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.repositories.whiteboard_repository import WhiteboardRepository
from app.models.whiteboard import Whiteboard
from app.models.user import User
from app.models.tag import Tag
from app.models.whiteboard_tag import WhiteboardTag
from app.models.collaborator import WhiteboardCollaborator, Permission
from app.core.security import get_password_hash


class TestWhiteboardRepository:
    """WhiteboardRepositoryのテストクラス"""
    
    @pytest.fixture
    def whiteboard_repository(self, db: Session):
        """テスト用WhiteboardRepositoryインスタンス"""
        return WhiteboardRepository(db)
    
    @pytest.fixture
    def sample_users(self, db: Session) -> list[User]:
        """テスト用ユーザーデータ"""
        users = [
            User(
                email="owner@example.com",
                name="Board Owner",
                password_hash=get_password_hash("password123")
            ),
            User(
                email="collaborator@example.com",
                name="Collaborator User",
                password_hash=get_password_hash("password123")
            ),
            User(
                email="other@example.com",
                name="Other User",
                password_hash=get_password_hash("password123")
            )
        ]
        
        db.add_all(users)
        db.commit()
        for user in users:
            db.refresh(user)
        return users
    
    @pytest.fixture
    def sample_tags(self, db: Session) -> list[Tag]:
        """テスト用タグデータ"""
        tags = [
            Tag(name="project", color="#FF0000", usage_count=10),
            Tag(name="design", color="#00FF00", usage_count=5),
            Tag(name="development", color="#0000FF", usage_count=8),
            Tag(name="testing", color="#FFFF00", usage_count=3),
        ]
        
        db.add_all(tags)
        db.commit()
        for tag in tags:
            db.refresh(tag)
        return tags
    
    # === 基本検索機能のテスト ===
    
    def test_find_by_filters_no_filters(self, whiteboard_repository, sample_users, db: Session):
        """フィルターなしでの検索テスト（全ホワイトボード取得）"""
        # Arrange
        owner = sample_users[0]
        
        # テストホワイトボードを作成
        wb1 = Whiteboard(title="Board 1", description="Description 1", owner_id=owner.id)
        wb2 = Whiteboard(title="Board 2", description="Description 2", owner_id=owner.id)
        wb3 = Whiteboard(title="Board 3", description="Description 3", owner_id=owner.id, is_public=True)
        
        db.add_all([wb1, wb2, wb3])
        db.commit()
        
        # Act
        results, total_count = whiteboard_repository.find_by_filters(user_id=owner.id)
        
        # Assert
        assert total_count == 3
        assert len(results) == 3
        assert all(wb.owner_id == owner.id for wb in results)
    
    def test_find_by_filters_tag_filter_single(self, whiteboard_repository, sample_users, sample_tags, db: Session):
        """単一タグフィルターでの検索テスト
        
        【テストの目的】
        特定のタグが付いたホワイトボードのみを検索できることを確認
        
        【テスト内容】
        - タグ付きホワイトボードとタグなしホワイトボードを作成
        - 特定のタグで検索した場合、該当するホワイトボードのみが返される
        - 実際のデータベースを使った統合テスト
        
        【学習ポイント】
        - データベースの関連テーブル（whiteboard_tags）の使い方
        - フィルター検索の仕組み（WHERE句での絞り込み）
        - テストデータの準備方法（関連データを含む）
        """
        # Arrange（準備フェーズ）
        # テスト用ユーザーとタグを取得
        owner = sample_users[0]        # テストユーザー（ホワイトボードの所有者）
        tag = sample_tags[0]           # テストタグ（"project" タグ）
        
        # 2つのホワイトボードを作成：1つはタグ付き、1つはタグなし
        wb_with_tag = Whiteboard(
            title="Tagged Board", 
            description="Board with project tag", 
            owner_id=owner.id
        )
        wb_without_tag = Whiteboard(
            title="Untagged Board", 
            description="Board without tags", 
            owner_id=owner.id
        )
        
        # データベースにホワイトボードを保存
        db.add_all([wb_with_tag, wb_without_tag])
        db.commit()  # データベースに永続化
        
        # ホワイトボードにタグを付与（中間テーブル whiteboard_tags を使用）
        wb_tag = WhiteboardTag(
            whiteboard_id=wb_with_tag.id,  # タグを付けるホワイトボード
            tag_id=tag.id                   # 付与するタグ
        )
        db.add(wb_tag)
        db.commit()  # タグ関連情報を永続化
        
        # Act（実行フェーズ）
        # 特定のタグで検索を実行
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=owner.id,      # 検索実行ユーザー
            tag_ids=[tag.id]       # 検索対象のタグID（リスト形式）
        )
        
        # Assert（検証フェーズ）
        # 検索結果が期待通りかを確認
        assert total_count == 1                       # 1件だけヒットする
        assert len(results) == 1                      # 結果リストに1件
        assert results[0].id == wb_with_tag.id        # タグ付きボードが返される
        assert results[0].title == "Tagged Board"     # 正しいタイトルが返される
    
    def test_find_by_filters_tag_filter_multiple_and_search(self, whiteboard_repository, sample_users, sample_tags, db: Session):
        """複数タグフィルター（AND検索）のテスト
        
        【テストの目的】
        複数のタグが"すべて"付いているホワイトボードのみを検索するAND検索の動作確認
        
        【テスト内容】
        - 異なるタグ組み合わせの3つのホワイトボードを作成
        - 2つのタグ（project AND design）で検索
        - 両方のタグを持つホワイトボードのみが結果に含まれる
        
        【学習ポイント】
        - AND検索とOR検索の違いの理解
        - 中間テーブルでの複数条件検索の仕組み
        - 実際のSQLクエリでのJOINとGROUP BYの使われ方
        """
        # Arrange（準備フェーズ）
        owner = sample_users[0]           # テストユーザー
        project_tag = sample_tags[0]      # "project" タグ
        design_tag = sample_tags[1]       # "design" タグ
        dev_tag = sample_tags[2]          # "development" タグ
        
        # 異なるタグ組み合わせの3つのホワイトボードを作成
        wb_project_design = Whiteboard(title="Project Design Board", owner_id=owner.id)  # project + design
        wb_project_only = Whiteboard(title="Project Only Board", owner_id=owner.id)     # project のみ
        wb_project_dev = Whiteboard(title="Project Dev Board", owner_id=owner.id)       # project + development
        
        # データベースにホワイトボードを保存
        db.add_all([wb_project_design, wb_project_only, wb_project_dev])
        db.commit()
        
        # 各ホワイトボードに異なるタグの組み合わせを付与
        # 【重要】AND検索をテストするため、意図的に異なる組み合わせを作成
        
        # Board 1: project + design（検索条件に完全一致）
        db.add_all([
            WhiteboardTag(whiteboard_id=wb_project_design.id, tag_id=project_tag.id),
            WhiteboardTag(whiteboard_id=wb_project_design.id, tag_id=design_tag.id)
        ])
        
        # Board 2: project のみ（design タグがないので検索結果に含まれない）
        db.add(WhiteboardTag(whiteboard_id=wb_project_only.id, tag_id=project_tag.id))
        
        # Board 3: project + development（design タグがないので検索結果に含まれない）
        db.add_all([
            WhiteboardTag(whiteboard_id=wb_project_dev.id, tag_id=project_tag.id),
            WhiteboardTag(whiteboard_id=wb_project_dev.id, tag_id=dev_tag.id)
        ])
        
        # データベースにタグ関連情報を永続化
        db.commit()
        
        # Act（実行フェーズ）
        # project AND design の両方を持つボードを検索
        # 【重要】AND検索なので、指定したタグを"すべて"持つボードのみが対象
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            tag_ids=[project_tag.id, design_tag.id]  # 両方のタグを指定
        )
        
        # Assert（検証フェーズ）
        # AND検索の結果を確認
        assert total_count == 1                         # project + design の両方を持つのは1つだけ
        assert len(results) == 1                       # 結果は1件
        assert results[0].id == wb_project_design.id   # 該当するボードが正しく返される
    
    def test_find_by_filters_author_filter_single(self, whiteboard_repository, sample_users, db: Session):
        """単一作成者フィルターでの検索テスト"""
        # Arrange
        owner1 = sample_users[0]
        owner2 = sample_users[1]
        searcher = sample_users[2]
        
        # 異なる作成者のホワイトボードを作成
        wb1 = Whiteboard(title="Owner 1 Board", owner_id=owner1.id, is_public=True)
        wb2 = Whiteboard(title="Owner 2 Board", owner_id=owner2.id, is_public=True)
        
        db.add_all([wb1, wb2])
        db.commit()
        
        # Act - owner1 のボードのみを検索
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=searcher.id,
            author_ids=[owner1.id]
        )
        
        # Assert
        assert total_count == 1
        assert len(results) == 1
        assert results[0].owner_id == owner1.id
        assert results[0].title == "Owner 1 Board"
    
    def test_find_by_filters_author_filter_multiple_or_search(self, whiteboard_repository, sample_users, db: Session):
        """複数作成者フィルター（OR検索）のテスト"""
        # Arrange
        owner1 = sample_users[0]
        owner2 = sample_users[1]
        other_user = sample_users[2]
        
        # 異なる作成者のホワイトボードを作成
        wb1 = Whiteboard(title="Owner 1 Board", owner_id=owner1.id, is_public=True)
        wb2 = Whiteboard(title="Owner 2 Board", owner_id=owner2.id, is_public=True)
        wb3 = Whiteboard(title="Other User Board", owner_id=other_user.id, is_public=True)
        
        db.add_all([wb1, wb2, wb3])
        db.commit()
        
        # Act - owner1 OR owner2 のボードを検索
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=owner1.id,  # 検索者
            author_ids=[owner1.id, owner2.id]
        )
        
        # Assert
        assert total_count == 2  # owner1 と owner2 のボード
        assert len(results) == 2
        owner_ids = {wb.owner_id for wb in results}
        assert owner_ids == {owner1.id, owner2.id}
    
    def test_find_by_filters_date_range_created(self, whiteboard_repository, sample_users, db: Session):
        """作成日範囲フィルターでの検索テスト"""
        # Arrange
        owner = sample_users[0]
        
        # 異なる作成日のホワイトボードを作成
        old_date = datetime.now() - timedelta(days=10)
        recent_date = datetime.now() - timedelta(days=2)
        
        wb_old = Whiteboard(title="Old Board", owner_id=owner.id)
        wb_recent = Whiteboard(title="Recent Board", owner_id=owner.id)
        
        db.add_all([wb_old, wb_recent])
        db.commit()
        db.refresh(wb_old)
        db.refresh(wb_recent)
        
        # SQLで作成日を更新（SQLAlchemyのカラム制約を回避）
        db.execute(
            text("UPDATE whiteboards SET created_at = :old_date WHERE id = :old_id"),
            {"old_date": old_date, "old_id": str(wb_old.id)}
        )
        db.execute(
            text("UPDATE whiteboards SET created_at = :recent_date WHERE id = :recent_id"),
            {"recent_date": recent_date, "recent_id": str(wb_recent.id)}
        )
        db.commit()
        
        # Act - 過去5日間のボードを検索
        search_from = datetime.now() - timedelta(days=5)
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            date_from=search_from
        )
        
        # Assert
        assert total_count == 1  # 最近のボードのみ
        assert len(results) == 1
        assert results[0].title == "Recent Board"
    
    # === 権限テスト ===
    
    def test_find_by_filters_owner_access(self, whiteboard_repository, sample_users, db: Session):
        """ホワイトボード所有者のアクセス権限テスト"""
        # Arrange
        owner = sample_users[0]
        other_user = sample_users[1]
        
        # 所有者のプライベートボード
        private_board = Whiteboard(title="Private Board", owner_id=owner.id, is_public=False)
        # 他のユーザーのプライベートボード
        other_private_board = Whiteboard(title="Other Private Board", owner_id=other_user.id, is_public=False)
        
        db.add_all([private_board, other_private_board])
        db.commit()
        
        # Act - 所有者として検索
        results, total_count = whiteboard_repository.find_by_filters(user_id=owner.id)
        
        # Assert
        assert total_count == 1  # 自分のボードのみアクセス可能
        assert len(results) == 1
        assert results[0].id == private_board.id
    
    def test_find_by_filters_public_access(self, whiteboard_repository, sample_users, db: Session):
        """パブリックホワイトボードのアクセス権限テスト"""
        # Arrange
        owner = sample_users[0]
        viewer = sample_users[1]
        
        # パブリックボード
        public_board = Whiteboard(title="Public Board", owner_id=owner.id, is_public=True)
        # プライベートボード
        private_board = Whiteboard(title="Private Board", owner_id=owner.id, is_public=False)
        
        db.add_all([public_board, private_board])
        db.commit()
        
        # Act - 他のユーザーとして検索
        results, total_count = whiteboard_repository.find_by_filters(user_id=viewer.id)
        
        # Assert
        assert total_count == 1  # パブリックボードのみアクセス可能
        assert len(results) == 1
        assert results[0].id == public_board.id
        assert results[0].is_public is True
    
    def test_find_by_filters_collaborator_access(self, whiteboard_repository, sample_users, db: Session):
        """コラボレーターアクセス権限テスト
        
        【テストの目的】
        ホワイトボードの権限システムが正しく動作することを確認
        
        【テスト内容】
        - プライベートホワイトボードを作成し、特定ユーザーにコラボレーター権限を付与
        - コラボレーターはアクセス可能、関係ないユーザーはアクセス不可を確認
        - セキュリティ要件の検証
        
        【学習ポイント】
        - データベースでの権限管理の仕組み
        - 中間テーブル（collaborators）での権限制御
        - セキュリティテストの重要性
        """
        # Arrange（準備フェーズ）
        # 3人のテストユーザーを準備
        owner = sample_users[0]           # ホワイトボードの所有者
        collaborator = sample_users[1]    # コラボレーター（権限あり）
        other_user = sample_users[2]      # 関係のないユーザー（権限なし）
        
        # プライベート（非公開）ホワイトボードを作成
        shared_board = Whiteboard(
            title="Shared Board", 
            owner_id=owner.id, 
            is_public=False  # 【重要】プライベート設定
        )
        db.add(shared_board)
        db.commit()  # ホワイトボードをデータベースに保存
        
        # コラボレーター権限を付与（collaborators テーブルに登録）
        collaboration = WhiteboardCollaborator(
            whiteboard_id=shared_board.id,     # 共有するホワイトボード
            user_id=collaborator.id,           # 権限を付与するユーザー
            permission=Permission.VIEW         # 閲覧権限
        )
        db.add(collaboration)
        db.commit()  # 権限情報をデータベースに保存
        
        # Act（実行フェーズ）
        # ケース1: コラボレーターとして検索（アクセス権限あり）
        results_collab, total_collab = whiteboard_repository.find_by_filters(
            user_id=collaborator.id
        )
        
        # ケース2: 関係のないユーザーとして検索（アクセス権限なし）
        results_other, total_other = whiteboard_repository.find_by_filters(
            user_id=other_user.id
        )
        
        # Assert（検証フェーズ）
        # ケース1の検証: コラボレーターはアクセス可能
        assert total_collab == 1                        # 1件アクセス可能
        assert len(results_collab) == 1                 # 結果に1件含まれる
        assert results_collab[0].id == shared_board.id  # 正しいボードが返される
        
        # ケース2の検証: 関係のないユーザーはアクセス不可
        assert total_other == 0                         # アクセス可能な件数は0
        assert len(results_other) == 0                  # 結果は空リスト
    
    # === ソート機能のテスト ===
    
    def test_find_by_filters_sort_by_created_at_desc(self, whiteboard_repository, sample_users, db: Session):
        """作成日降順ソートのテスト"""
        # Arrange
        owner = sample_users[0]
        
        # 異なる作成日のホワイトボードを作成
        wb_old = Whiteboard(title="Old Board", owner_id=owner.id)
        wb_new = Whiteboard(title="New Board", owner_id=owner.id)
        
        db.add_all([wb_old, wb_new])
        db.commit()
        db.refresh(wb_old)
        db.refresh(wb_new)
        
        # SQLで作成日を設定
        old_date = datetime.now() - timedelta(days=5)
        new_date = datetime.now() - timedelta(days=1)
        
        db.execute(
            text("UPDATE whiteboards SET created_at = :old_date WHERE id = :old_id"),
            {"old_date": old_date, "old_id": str(wb_old.id)}
        )
        db.execute(
            text("UPDATE whiteboards SET created_at = :new_date WHERE id = :new_id"),
            {"new_date": new_date, "new_id": str(wb_new.id)}
        )
        db.commit()
        
        # Act
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            sort_by="created_at",
            sort_order="desc"
        )
        
        # Assert
        assert total_count == 2
        assert len(results) == 2
        assert results[0].title == "New Board"  # 新しいボードが最初
        assert results[1].title == "Old Board"  # 古いボードが後
    
    def test_find_by_filters_sort_by_title_asc(self, whiteboard_repository, sample_users, db: Session):
        """タイトル昇順ソートのテスト"""
        # Arrange
        owner = sample_users[0]
        
        wb_z = Whiteboard(title="Z Board", owner_id=owner.id)
        wb_a = Whiteboard(title="A Board", owner_id=owner.id)
        wb_m = Whiteboard(title="M Board", owner_id=owner.id)
        
        db.add_all([wb_z, wb_a, wb_m])
        db.commit()
        
        # Act
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            sort_by="title",
            sort_order="asc"
        )
        
        # Assert
        assert total_count == 3
        assert len(results) == 3
        assert results[0].title == "A Board"
        assert results[1].title == "M Board"
        assert results[2].title == "Z Board"
    
    # === ページネーション機能のテスト ===
    
    def test_find_by_filters_pagination(self, whiteboard_repository, sample_users, db: Session):
        """ページネーション機能のテスト"""
        # Arrange
        owner = sample_users[0]
        
        # 15個のホワイトボードを作成
        whiteboards = []
        for i in range(15):
            wb = Whiteboard(title=f"Board {i:02d}", owner_id=owner.id)
            whiteboards.append(wb)
        
        db.add_all(whiteboards)
        db.commit()
        
        # Act - 1ページ目（10件）
        results_page1, total_page1 = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            limit=10,
            offset=0
        )
        
        # Act - 2ページ目（残り5件）
        results_page2, total_page2 = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            limit=10,
            offset=10
        )
        
        # Assert
        assert total_page1 == 15
        assert len(results_page1) == 10
        
        assert total_page2 == 15  # 総数は同じ
        assert len(results_page2) == 5  # 残り5件
        
        # 重複がないことを確認
        page1_ids = {wb.id for wb in results_page1}
        page2_ids = {wb.id for wb in results_page2}
        assert len(page1_ids.intersection(page2_ids)) == 0
    
    # === 利用可能データ取得のテスト ===
    
    def test_get_distinct_tags(self, whiteboard_repository, sample_users, sample_tags, db: Session):
        """アクセス可能なタグ一覧取得のテスト"""
        # Arrange
        owner = sample_users[0]
        other_user = sample_users[1]
        
        # 所有者のボードにタグを付与
        wb_owner = Whiteboard(title="Owner Board", owner_id=owner.id, is_public=False)
        # 他のユーザーのプライベートボードにタグを付与（アクセス不可）
        wb_other_private = Whiteboard(title="Other Private Board", owner_id=other_user.id, is_public=False)
        # 他のユーザーのパブリックボードにタグを付与（アクセス可能）
        wb_other_public = Whiteboard(title="Other Public Board", owner_id=other_user.id, is_public=True)
        
        db.add_all([wb_owner, wb_other_private, wb_other_public])
        db.commit()
        
        # タグを付与
        project_tag = sample_tags[0]  # "project"
        design_tag = sample_tags[1]   # "design"
        dev_tag = sample_tags[2]      # "development"
        
        db.add_all([
            WhiteboardTag(whiteboard_id=wb_owner.id, tag_id=project_tag.id),
            WhiteboardTag(whiteboard_id=wb_other_private.id, tag_id=design_tag.id),  # アクセス不可
            WhiteboardTag(whiteboard_id=wb_other_public.id, tag_id=dev_tag.id),     # アクセス可能
        ])
        db.commit()
        
        # Act
        available_tags = whiteboard_repository.get_distinct_tags(owner.id)
        
        # Assert
        assert len(available_tags) == 2  # project（自分のボード）+ development（パブリック）
        tag_names = {tag.name for tag in available_tags}
        assert "project" in tag_names
        assert "development" in tag_names
        assert "design" not in tag_names  # プライベートなので除外
    
    def test_get_distinct_authors(self, whiteboard_repository, sample_users, db: Session):
        """アクセス可能な作成者一覧取得のテスト"""
        # Arrange
        owner = sample_users[0]
        collaborator = sample_users[1]
        other_user = sample_users[2]
        
        # 異なるアクセス権限のホワイトボードを作成
        wb_own = Whiteboard(title="Own Board", owner_id=owner.id, is_public=False)
        wb_collab = Whiteboard(title="Collab Board", owner_id=collaborator.id, is_public=False)
        wb_public = Whiteboard(title="Public Board", owner_id=other_user.id, is_public=True)
        
        db.add_all([wb_own, wb_collab, wb_public])
        db.commit()
        
        # コラボレーション権限を設定
        collaboration = WhiteboardCollaborator(
            whiteboard_id=wb_collab.id,
            user_id=owner.id,
            permission=Permission.VIEW
        )
        db.add(collaboration)
        db.commit()
        
        # Act
        available_authors = whiteboard_repository.get_distinct_authors(owner.id)
        
        # Assert
        assert len(available_authors) == 3  # 自分 + コラボレーター + パブリック作成者
        author_names = {author.name for author in available_authors}
        assert "Board Owner" in author_names
        assert "Collaborator User" in author_names
        assert "Other User" in author_names
    
    # === 複合フィルターのテスト ===
    
    def test_find_by_filters_complex_combination(self, whiteboard_repository, sample_users, sample_tags, db: Session):
        """複合フィルター（タグ + 作成者 + 日付範囲）のテスト"""
        # Arrange
        owner = sample_users[0]
        other_owner = sample_users[1]
        searcher = sample_users[2]
        
        project_tag = sample_tags[0]
        design_tag = sample_tags[1]
        
        # 条件に合うボード
        target_board = Whiteboard(
            title="Target Board", 
            owner_id=owner.id, 
            is_public=True
        )
        
        # 条件に合わないボード（古い日付）
        old_board = Whiteboard(
            title="Old Board", 
            owner_id=owner.id, 
            is_public=True
        )
        
        # 条件に合わないボード（異なる作成者）
        wrong_author_board = Whiteboard(
            title="Wrong Author Board", 
            owner_id=other_owner.id, 
            is_public=True
        )
        
        db.add_all([target_board, old_board, wrong_author_board])
        db.commit()
        db.refresh(target_board)
        db.refresh(old_board)
        db.refresh(wrong_author_board)
        
        # SQLで作成日を設定
        target_date = datetime.now() - timedelta(days=2)
        old_date = datetime.now() - timedelta(days=10)
        wrong_date = datetime.now() - timedelta(days=1)
        
        db.execute(
            text("UPDATE whiteboards SET created_at = :date WHERE id = :id"),
            {"date": target_date, "id": str(target_board.id)}
        )
        db.execute(
            text("UPDATE whiteboards SET created_at = :date WHERE id = :id"),
            {"date": old_date, "id": str(old_board.id)}
        )
        db.execute(
            text("UPDATE whiteboards SET created_at = :date WHERE id = :id"),
            {"date": wrong_date, "id": str(wrong_author_board.id)}
        )
        db.commit()
        
        # タグを付与
        db.add_all([
            WhiteboardTag(whiteboard_id=target_board.id, tag_id=project_tag.id),
            WhiteboardTag(whiteboard_id=target_board.id, tag_id=design_tag.id),
            WhiteboardTag(whiteboard_id=old_board.id, tag_id=project_tag.id),
            WhiteboardTag(whiteboard_id=old_board.id, tag_id=design_tag.id),
            WhiteboardTag(whiteboard_id=wrong_author_board.id, tag_id=project_tag.id),
            WhiteboardTag(whiteboard_id=wrong_author_board.id, tag_id=design_tag.id),
        ])
        db.commit()
        
        # Act - 複合条件での検索
        search_from = datetime.now() - timedelta(days=5)
        search_to = datetime.now()
        
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=searcher.id,
            tag_ids=[project_tag.id, design_tag.id],  # AND: project AND design
            author_ids=[owner.id],                     # 特定の作成者
            date_from=search_from,                     # 日付範囲
            date_to=search_to
        )
        
        # Assert
        assert total_count == 1  # 全条件を満たすのは target_board のみ
        assert len(results) == 1
        assert results[0].id == target_board.id
    
    # === エッジケース ===
    
    def test_count_by_filters_consistency(self, whiteboard_repository, sample_users, sample_tags, db: Session):
        """count_by_filters と find_by_filters の一貫性テスト"""
        # Arrange
        owner = sample_users[0]
        tag = sample_tags[0]
        
        # テストデータを作成
        wb1 = Whiteboard(title="Board 1", owner_id=owner.id)
        wb2 = Whiteboard(title="Board 2", owner_id=owner.id)
        
        db.add_all([wb1, wb2])
        db.commit()
        
        # 1つのボードにのみタグを付与
        wb_tag = WhiteboardTag(whiteboard_id=wb1.id, tag_id=tag.id)
        db.add(wb_tag)
        db.commit()
        
        # Act
        results, find_count = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            tag_ids=[tag.id]
        )
        
        count_result = whiteboard_repository.count_by_filters(
            user_id=owner.id,
            tag_ids=[tag.id]
        )
        
        # Assert - 件数が一致することを確認
        assert find_count == count_result == 1
        assert len(results) == 1
    
    def test_find_by_filters_soft_deleted_tags(self, whiteboard_repository, sample_users, sample_tags, db: Session):
        """論理削除されたタグは検索結果に含まれないことのテスト"""
        # Arrange
        owner = sample_users[0]
        tag = sample_tags[0]
        
        # ホワイトボードとタグ関連を作成
        wb = Whiteboard(title="Board with Deleted Tag", owner_id=owner.id)
        db.add(wb)
        db.commit()
        
        # タグを付与してから論理削除
        wb_tag = WhiteboardTag(whiteboard_id=wb.id, tag_id=tag.id)
        wb_tag.deleted_at = datetime.now()  # 論理削除
        db.add(wb_tag)
        db.commit()
        
        # Act - 削除されたタグで検索
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            tag_ids=[tag.id]
        )
        
        # Assert - 論理削除されたタグは検索結果に含まれない
        assert total_count == 0
        assert len(results) == 0
    
    def test_find_by_filters_empty_database(self, whiteboard_repository, sample_users, db: Session):
        """空のデータベースでの検索テスト"""
        # Arrange
        owner = sample_users[0]
        
        # Act - ホワイトボードが存在しない状態で検索
        results, total_count = whiteboard_repository.find_by_filters(user_id=owner.id)
        
        # Assert
        assert total_count == 0
        assert len(results) == 0
        assert isinstance(results, list)
    
    # === 境界値テスト ===
    
    def test_find_by_filters_large_limit(self, whiteboard_repository, sample_users, db: Session):
        """大きなlimit値での検索テスト"""
        # Arrange
        owner = sample_users[0]
        
        # 5個のホワイトボードを作成
        whiteboards = []
        for i in range(5):
            wb = Whiteboard(title=f"Board {i}", owner_id=owner.id)
            whiteboards.append(wb)
        
        db.add_all(whiteboards)
        db.commit()
        
        # Act - limit=1000（実際のデータより多い）
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            limit=1000
        )
        
        # Assert
        assert total_count == 5
        assert len(results) == 5  # 実際のデータ数に制限される
    
    def test_find_by_filters_zero_limit(self, whiteboard_repository, sample_users, db: Session):
        """limit=0での検索テスト"""
        # Arrange
        owner = sample_users[0]
        
        wb = Whiteboard(title="Test Board", owner_id=owner.id)
        db.add(wb)
        db.commit()
        
        # Act
        results, total_count = whiteboard_repository.find_by_filters(
            user_id=owner.id,
            limit=0
        )
        
        # Assert
        assert total_count == 1  # 総数は正しく計算される
        assert len(results) == 0  # limit=0なので結果は空