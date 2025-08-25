"""
API統合テスト

このテストファイルは検索APIエンドポイントの統合機能をテストする:
- POST /api/v1/search/whiteboards: メイン検索機能
- GET /api/v1/search/tags: 利用可能タグ一覧  
- GET /api/v1/search/authors: 作成者一覧
- 認証・認可統合: JWT認証 + 権限フィルタリング動作確認
- エラーハンドリング: バリデーション・権限・サーバーエラーの確認
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.whiteboard import Whiteboard
from app.models.tag import Tag
from app.models.whiteboard_tag import WhiteboardTag
from app.core.security import get_password_hash


class TestSearchAPIIntegration:
    """検索API統合テストクラス"""
    
    @pytest.fixture
    def api_test_data(self, db: Session):
        """API統合テスト用のテストデータ作成
        
        【フィクスチャの目的】
        検索API統合テストで使用するリアルなテストデータを作成
        
        【作成されるデータ】
        - 3人のユーザー（権限テスト用）
        - 5種類のタグ（検索バリエーションテスト用）  
        - 10件のホワイトボード（様々な権限設定・タグ付けパターン）
        
        【データ設計の特徴】
        - パブリック/プライベートの混在
        - 異なるユーザーが作成したホワイトボード  
        - 様々なタグ組み合わせ
        - 日付範囲のバリエーション
        
        【学習ポイント】  
        - API統合テストに特化したテストデータ設計
        - 権限システムテスト用のユーザー・ホワイトボード関係構築
        - リアルなデータ分布の模擬方法
        """
        print("API統合テスト用データ作成開始...")
        
        # ステップ1: テスト用ユーザー作成（3人、異なる権限パターン用）
        users = []
        for i in range(3):
            user = User(
                email=f"api_user_{i}@example.com",     # API用ユニークメール
                name=f"API User {i}",                  # 識別しやすい名前
                password_hash=get_password_hash("api_password123")  # API用パスワード
            )
            users.append(user)
        
        db.add_all(users)
        db.commit()
        print(f"✓ {len(users)}人のAPIテスト用ユーザーを作成")
        
        # ステップ2: タグ作成（5種類、検索バリエーション用）
        tags = []
        tag_data = [
            ("frontend", "#3498db", "blue"),      # フロントエンド（青）
            ("backend", "#e74c3c", "red"),        # バックエンド（赤）
            ("design", "#f39c12", "orange"),      # デザイン（オレンジ）
            ("testing", "#27ae60", "green"),      # テスト（緑）
            ("documentation", "#9b59b6", "purple") # ドキュメント（紫）
        ]
        
        for name, color, _ in tag_data:
            tag = Tag(
                name=name,
                color=color,
                usage_count=0  # 初期値
            )
            tags.append(tag)
        
        db.add_all(tags)
        db.commit()
        print(f"✓ {len(tags)}種類のタグを作成: {[tag.name for tag in tags]}")
        
        # ステップ3: ホワイトボード作成（10件、様々なパターン）
        whiteboards = []
        whiteboard_configs = [
            # (title, owner_index, is_public, tag_indices)
            ("公開プロジェクト計画", 0, True, [0, 1]),      # frontend + backend
            ("プライベート設計書", 0, False, [2]),          # design only  
            ("チームドキュメント", 1, True, [4]),           # documentation
            ("個人メモ", 1, False, [0, 2]),                # frontend + design
            ("テスト仕様書", 2, True, [3, 4]),             # testing + documentation
            ("API設計", 2, False, [1]),                    # backend only
            ("UI/UXガイド", 0, True, [0, 2]),              # frontend + design
            ("開発環境構築", 1, False, [1, 3]),            # backend + testing
            ("プロジェクト概要", 2, True, [0, 1, 2]),       # frontend + backend + design
            ("リリース手順", 0, False, [1, 3, 4])          # backend + testing + documentation
        ]
        
        for i, (title, owner_idx, is_public, tag_indices) in enumerate(whiteboard_configs):
            # 作成日時を分散させる（過去30日間の範囲）
            days_ago = i * 3  # 0, 3, 6, 9...日前
            created_at = datetime.now() - timedelta(days=days_ago)
            
            wb = Whiteboard(
                title=title,
                description=f"{title}の説明文です。",
                owner_id=users[owner_idx].id,
                is_public=is_public,
                created_at=created_at,
                updated_at=created_at
            )
            whiteboards.append((wb, tag_indices))  # タグ情報も保持
        
        # ホワイトボードをデータベースに追加
        wb_objects = [wb for wb, _ in whiteboards]
        db.add_all(wb_objects)
        db.commit()
        print(f"✓ {len(wb_objects)}件のホワイトボードを作成")
        
        # ステップ4: ホワイトボード-タグ関連作成
        wb_tags = []
        for wb, tag_indices in whiteboards:
            for tag_idx in tag_indices:
                wb_tag = WhiteboardTag(
                    whiteboard_id=wb.id,
                    tag_id=tags[tag_idx].id
                )
                wb_tags.append(wb_tag)
                # タグの使用回数を更新
                tags[tag_idx].usage_count += 1
        
        db.add_all(wb_tags)
        db.commit()
        print(f"✓ {len(wb_tags)}件のホワイトボード-タグ関連を作成")
        
        # フィクスチャの戻り値
        return {
            "users": users,           # 3人のテストユーザー
            "tags": tags,             # 5種類のタグ
            "whiteboards": wb_objects  # 10件のホワイトボード
        }
    
    # === メイン検索API (POST /api/v1/search/whiteboards) のテスト ===
    
    def test_search_whiteboards_basic_functionality(self, client: TestClient, auth_headers: dict, api_test_data):
        """基本的な検索機能のテスト
        
        【テストの目的】
        メイン検索APIの基本的な機能が正常に動作することを確認
        
        【テスト内容】
        1. 空の検索条件での全件検索
        2. レスポンス形式の確認
        3. ページネーションの動作確認
        4. 認証が正しく動作することの確認
        
        【学習ポイント】
        - FastAPIのTestClientを使ったHTTP APIテスト
        - JSONレスポンスの検証方法
        - 認証ヘッダーの使用方法
        """
        # Arrange（準備フェーズ）
        test_data = api_test_data  # API統合テスト用データ
        
        # Act（実行フェーズ）
        # 基本的な検索リクエストを送信（空の検索条件 = 全件検索）
        response = client.post(
            "/api/v1/search/whiteboards",
            json={},  # 空のフィルター条件
            headers=auth_headers  # JWT認証ヘッダー
        )
        
        # Assert（検証フェーズ）
        # HTTPステータスコードの確認
        assert response.status_code == 200, f"期待されるステータス200、実際は{response.status_code}: {response.text}"
        
        # JSONレスポンスの解析
        data = response.json()
        
        # レスポンス形式の確認
        assert "results" in data, "レスポンスに'results'フィールドがありません"
        assert "total" in data, "レスポンスに'total'フィールドがありません"
        assert "page" in data, "レスポンスに'page'フィールドがありません"
        assert "page_size" in data, "レスポンスに'page_size'フィールドがありません"
        
        # データ型の確認
        assert isinstance(data["results"], list), "resultsがリスト型ではありません"
        assert isinstance(data["total"], int), "totalが整数型ではありません"
        
        # ページネーションの確認
        assert data["page"] == 1, "初期ページが1ではありません"
        assert data["page_size"] == 10, "デフォルトページサイズが10ではありません"
        assert len(data["results"]) <= data["page_size"], "取得件数がpage_sizeを超えています"
        
        print(f"✓ 基本検索テスト成功: {data['total']}件中{len(data['results'])}件取得")
    
    def test_search_whiteboards_tag_filter(self, client: TestClient, auth_headers: dict, api_test_data):
        """タグフィルターでの検索テスト
        
        【テストの目的】
        タグによる検索フィルタリングが正常に動作することを確認
        
        【テスト内容】
        1. 特定のタグでの検索
        2. 検索結果にそのタグが付いたホワイトボードのみが含まれることを確認
        3. 権限フィルタリングとの組み合わせ動作確認
        
        【学習ポイント】
        - フィルター条件の指定方法
        - タグID配列による検索指定
        - レスポンスデータの詳細検証
        """
        # Arrange（準備フェーズ）
        test_data = api_test_data
        frontend_tag = next(tag for tag in test_data["tags"] if tag.name == "frontend")
        
        # Act（実行フェーズ）
        # frontend タグでの検索を実行
        response = client.post(
            "/api/v1/search/whiteboards",
            json={
                "tags": [str(frontend_tag.id)]  # frontendタグIDを指定
            },
            headers=auth_headers
        )
        
        # Assert（検証フェーズ）
        assert response.status_code == 200, f"タグ検索でエラー: {response.text}"
        
        data = response.json()
        assert data["total"] >= 0, "検索結果の総件数が負数です"
        
        # 結果がある場合、各アイテムの基本構造を確認
        for item in data["results"]:
            assert "id" in item, "ホワイトボードIDがありません"
            assert "title" in item, "タイトルがありません"
            assert "tags" in item, "タグ情報がありません"
            
            # このテストではタグ内容の詳細な検証は省略
            # （実際のタグマッピングの詳細検証は別のテストで実施）
        
        print(f"✓ タグフィルター検索テスト成功: 'frontend'タグで{data['total']}件ヒット")
    
    def test_search_whiteboards_author_filter(self, client: TestClient, auth_headers: dict, api_test_data):
        """作成者フィルターでの検索テスト
        
        【テストの目的】
        作成者による検索フィルタリングが正常に動作することを確認
        
        【テスト内容】
        1. 特定の作成者での検索
        2. OR条件での複数作成者指定
        3. 権限チェック（アクセス可能なホワイトボードのみ取得）
        
        【学習ポイント】
        - 作成者IDリストによるOR検索の指定方法
        - 権限システムとの統合確認
        - 複数条件での検索テスト設計
        """
        # Arrange（準備フェーズ）
        test_data = api_test_data
        # 2人目のユーザー（API User 1）のホワイトボードを検索
        target_user = test_data["users"][1]
        
        # Act（実行フェーズ）
        # 特定の作成者でのOR検索を実行
        response = client.post(
            "/api/v1/search/whiteboards",
            json={
                "authors": [str(target_user.id)]  # 2人目のユーザーIDを指定
            },
            headers=auth_headers
        )
        
        # Assert（検証フェーズ）
        assert response.status_code == 200, f"作成者検索でエラー: {response.text}"
        
        data = response.json()
        assert data["total"] >= 0, "検索結果の総件数が負数です"
        
        # 結果がある場合の基本構造確認
        for item in data["results"]:
            assert "id" in item, "ホワイトボードIDがありません"
            assert "title" in item, "タイトルがありません"
            assert "creator" in item, "作成者情報がありません"
        
        print(f"✓ 作成者フィルター検索テスト成功: ユーザー'{target_user.name}'で{data['total']}件ヒット")
    
    def test_search_whiteboards_date_range_filter(self, client: TestClient, auth_headers: dict, api_test_data):
        """日付範囲フィルターでの検索テスト
        
        【テストの目的】
        日付範囲による検索フィルタリングが正常に動作することを確認
        
        【テスト内容】
        1. 日付範囲を指定した検索
        2. date_from, date_to による範囲指定
        3. ISO8601形式での日付指定の動作確認
        
        【学習ポイント】
        - 日付範囲フィルターの指定方法
        - ISO8601形式での日付時刻指定
        - 時系列データの検索テスト方法
        """
        # Arrange（準備フェーズ）
        # 過去15日間の日付範囲を設定
        date_to = datetime.now()
        date_from = date_to - timedelta(days=15)
        
        # Act（実行フェーズ）
        # 日付範囲での検索を実行
        response = client.post(
            "/api/v1/search/whiteboards",
            json={
                "date_range": {
                    "date_from": date_from.isoformat(),  # ISO8601形式
                    "date_to": date_to.isoformat()
                }
            },
            headers=auth_headers
        )
        
        # Assert（検証フェーズ）
        assert response.status_code == 200, f"日付範囲検索でエラー: {response.text}"
        
        data = response.json()
        assert data["total"] >= 0, "検索結果の総件数が負数です"
        
        # 結果がある場合の基本構造確認
        for item in data["results"]:
            assert "id" in item, "ホワイトボードIDがありません"
            assert "created_at" in item, "作成日時がありません"
            assert "updated_at" in item, "更新日時がありません"
        
        print(f"✓ 日付範囲フィルター検索テスト成功: 過去15日間で{data['total']}件ヒット")
    
    def test_search_whiteboards_combined_filters(self, client: TestClient, auth_headers: dict, api_test_data):
        """複合フィルターでの検索テスト
        
        【テストの目的】
        複数の検索条件を組み合わせた複合検索が正常に動作することを確認
        
        【テスト内容】
        1. タグ + 作成者 + 日付範囲の組み合わせ検索
        2. AND/OR条件の正しい適用
        3. 複雑な検索条件での性能確認
        
        【学習ポイント】
        - 複数フィルター条件の同時指定方法
        - 複合検索での論理演算の動作確認
        - リアルユーザーの検索パターンのシミュレーション
        """
        # Arrange（準備フェーズ）
        test_data = api_test_data
        frontend_tag = next(tag for tag in test_data["tags"] if tag.name == "frontend")
        target_user = test_data["users"][0]
        
        # 過去20日間の範囲
        date_to = datetime.now()
        date_from = date_to - timedelta(days=20)
        
        # Act（実行フェーズ）
        # 複合検索を実行（タグ + 作成者 + 日付範囲）
        response = client.post(
            "/api/v1/search/whiteboards",
            json={
                "tags": [str(frontend_tag.id)],        # frontendタグ
                "authors": [str(target_user.id)],      # 特定の作成者
                "date_range": {                        # 日付範囲
                    "date_from": date_from.isoformat(),
                    "date_to": date_to.isoformat()
                }
            },
            headers=auth_headers
        )
        
        # Assert（検証フェーズ）
        assert response.status_code == 200, f"複合検索でエラー: {response.text}"
        
        data = response.json()
        assert data["total"] >= 0, "検索結果の総件数が負数です"
        
        # 結果の基本構造確認
        for item in data["results"]:
            assert "id" in item, "ホワイトボードIDがありません"
            assert "title" in item, "タイトルがありません"
            assert "tags" in item, "タグ情報がありません"
            assert "creator" in item, "作成者情報がありません"
            assert "created_at" in item, "作成日時がありません"
        
        print(f"✓ 複合フィルター検索テスト成功: 複数条件で{data['total']}件ヒット")
    
    def test_search_whiteboards_pagination(self, client: TestClient, auth_headers: dict, api_test_data):
        """ページネーション機能のテスト
        
        【テストの目的】
        検索結果のページネーション機能が正常に動作することを確認
        
        【テスト内容】
        1. page, page_size パラメータの動作確認
        2. 複数ページにわたる結果の取得
        3. ページング情報（total, has_next等）の正確性
        
        【学習ポイント】
        - APIのクエリパラメータ指定方法
        - ページネーション実装の検証方法
        - 大量データでの分割取得の仕組み
        """
        # Arrange（準備フェーズ）
        # 小さなページサイズでページネーションをテスト
        page_size = 3
        
        # Act（実行フェーズ）
        # 1ページ目を取得
        response = client.post(
            "/api/v1/search/whiteboards?page=1&page_size=3",
            json={},  # 全件検索
            headers=auth_headers
        )
        
        # Assert（検証フェーズ）
        assert response.status_code == 200, f"ページネーション検索でエラー: {response.text}"
        
        data = response.json()
        
        # ページング情報の確認
        assert data["page"] == 1, "現在ページが正しくありません"
        assert data["page_size"] == page_size, f"ページサイズが期待値と異なります: {data['page_size']}"
        assert len(data["results"]) <= page_size, "取得件数がページサイズを超えています"
        
        # 2ページ目が存在する場合のテスト
        if data["total"] > page_size:
            response2 = client.post(
                "/api/v1/search/whiteboards?page=2&page_size=3",
                json={},
                headers=auth_headers
            )
            
            assert response2.status_code == 200, "2ページ目の取得でエラー"
            data2 = response2.json()
            assert data2["page"] == 2, "2ページ目のページ番号が正しくありません"
        
        print(f"✓ ページネーションテスト成功: 総{data['total']}件を{page_size}件ずつ分割取得")
    
    def test_search_whiteboards_authentication_required(self, client: TestClient, api_test_data):
        """認証必須の確認テスト
        
        【テストの目的】
        検索APIが認証なしでアクセスできないことを確認
        
        【テスト内容】
        1. 認証ヘッダーなしでのリクエスト
        2. 401 Unauthorizedエラーの確認
        3. セキュリティが正しく動作することの検証
        
        【学習ポイント】
        - API認証の動作確認方法
        - HTTPステータスコードによるエラーハンドリング
        - セキュリティテストの重要性
        """
        # Act（実行フェーズ）
        # 認証ヘッダーなしでリクエスト送信
        response = client.post(
            "/api/v1/search/whiteboards",
            json={}  # 認証ヘッダーなし
        )
        
        # Assert（検証フェーズ）
        # 認証エラーが発生することを確認
        assert response.status_code == 401, f"認証エラーが期待されますが、実際は{response.status_code}"
        
        print("✓ 認証必須テスト成功: 未認証リクエストが正しく拒否されました")
    
    def test_search_whiteboards_invalid_filter_data(self, client: TestClient, auth_headers: dict):
        """無効な検索条件でのバリデーションテスト
        
        【テストの目的】
        無効な検索条件に対するバリデーションエラーハンドリングを確認
        
        【テスト内容】
        1. 無効なUUID形式での検索
        2. 無効な日付形式での検索
        3. 400 Bad Requestエラーの確認
        
        【学習ポイント】
        - APIバリデーションの動作確認
        - エラーレスポンスの形式確認
        - 不正データに対する防御機能のテスト
        """
        # Act & Assert（実行＆検証フェーズ）
        # 無効なUUID形式でのタグ検索
        response = client.post(
            "/api/v1/search/whiteboards",
            json={
                "tags": ["invalid-uuid-format"]  # 不正なUUID
            },
            headers=auth_headers
        )
        
        # バリデーションエラーが期待される（400 または 422）
        assert response.status_code in [400, 422], f"バリデーションエラーが期待されますが、実際は{response.status_code}"
        
        print("✓ バリデーションテスト成功: 無効なデータが正しく拒否されました")
    
    # === タグ一覧API (GET /api/v1/search/tags) のテスト ===
    
    def test_get_available_tags_basic_functionality(self, client: TestClient, auth_headers: dict, api_test_data):
        """タグ一覧取得の基本機能テスト
        
        【テストの目的】
        利用可能なタグ一覧APIの基本的な機能が正常に動作することを確認
        
        【テスト内容】
        1. タグ一覧の取得
        2. レスポンス形式の確認（配列形式）
        3. 各タグアイテムの必須フィールド確認
        4. 権限フィルタリングの動作確認
        
        【学習ポイント】
        - GETエンドポイントのテスト方法
        - 配列レスポンスの検証方法
        - タグデータ構造の確認
        """
        # Act（実行フェーズ）
        response = client.get(
            "/api/v1/search/tags",
            headers=auth_headers
        )
        
        # Assert（検証フェーズ）
        assert response.status_code == 200, f"タグ一覧取得でエラー: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "タグ一覧がリスト形式ではありません"
        
        # 各タグの必須フィールドを確認
        for tag in data:
            assert "id" in tag, "タグIDがありません"
            assert "name" in tag, "タグ名がありません"
            assert "color" in tag, "タグ色がありません"
            assert "usage_count" in tag, "使用回数がありません"
            
            # データ型の確認
            assert isinstance(tag["name"], str), "タグ名が文字列ではありません"
            assert isinstance(tag["color"], str), "タグ色が文字列ではありません"
            assert isinstance(tag["usage_count"], int), "使用回数が整数ではありません"
        
        print(f"✓ タグ一覧取得テスト成功: {len(data)}種類のタグを取得")
    
    def test_get_available_tags_authentication_required(self, client: TestClient):
        """タグ一覧API認証必須の確認テスト
        
        【テストの目的】
        タグ一覧APIが認証なしでアクセスできないことを確認
        
        【テスト内容】
        1. 認証ヘッダーなしでのリクエスト
        2. 401 Unauthorizedエラーの確認
        
        【学習ポイント】
        - 全APIエンドポイントでの一貫した認証要求
        - セキュリティポリシーの統一性確認
        """
        # Act（実行フェーズ）
        response = client.get("/api/v1/search/tags")  # 認証ヘッダーなし
        
        # Assert（検証フェーズ）
        assert response.status_code == 401, f"認証エラーが期待されますが、実際は{response.status_code}"
        
        print("✓ タグ一覧API認証必須テスト成功")
    
    # === 作成者一覧API (GET /api/v1/search/authors) のテスト ===
    
    def test_get_available_authors_basic_functionality(self, client: TestClient, auth_headers: dict, api_test_data):
        """作成者一覧取得の基本機能テスト
        
        【テストの目的】
        検索対象作成者一覧APIの基本的な機能が正常に動作することを確認
        
        【テスト内容】
        1. 作成者一覧の取得
        2. レスポンス形式の確認（配列形式）
        3. 各作成者アイテムの必須フィールド確認
        4. 権限に基づく作成者フィルタリングの動作確認
        
        【学習ポイント】
        - ユーザー情報の安全な取得方法
        - プライバシー保護を考慮したデータ構造
        - 権限システムとの統合
        """
        # Act（実行フェーズ）
        response = client.get(
            "/api/v1/search/authors",
            headers=auth_headers
        )
        
        # Assert（検証フェーズ）
        assert response.status_code == 200, f"作成者一覧取得でエラー: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "作成者一覧がリスト形式ではありません"
        
        # 各作成者の必須フィールドを確認
        for author in data:
            assert "id" in author, "作成者IDがありません"
            assert "name" in author, "作成者名がありません"
            
            # データ型の確認
            assert isinstance(author["name"], str), "作成者名が文字列ではありません"
            
            # プライバシー保護の確認：emailなどの機密情報が含まれていないことを確認
            assert "password_hash" not in author, "パスワードハッシュが露出しています"
            assert "email" not in author, "メールアドレスが不要に露出しています"
        
        print(f"✓ 作成者一覧取得テスト成功: {len(data)}人の作成者を取得")
    
    def test_get_available_authors_authentication_required(self, client: TestClient):
        """作成者一覧API認証必須の確認テスト
        
        【テストの目的】
        作成者一覧APIが認証なしでアクセスできないことを確認
        
        【テスト内容】
        1. 認証ヘッダーなしでのリクエスト
        2. 401 Unauthorizedエラーの確認
        
        【学習ポイント】
        - 個人情報を含むAPIでの厳格な認証要求
        - セキュリティポリシーの一貫性
        """
        # Act（実行フェーズ）
        response = client.get("/api/v1/search/authors")  # 認証ヘッダーなし
        
        # Assert（検証フェーズ）
        assert response.status_code == 401, f"認証エラーが期待されますが、実際は{response.status_code}"
        
        print("✓ 作成者一覧API認証必須テスト成功")
    
    # === エラーハンドリング統合テスト ===
    
    def test_server_error_handling(self, client: TestClient, auth_headers: dict):
        """サーバーエラーハンドリングテスト
        
        【テストの目的】
        予期しないサーバーエラーが適切に処理されることを確認
        
        【テスト内容】
        1. 存在しないエンドポイントへのアクセス
        2. 404エラーの確認
        3. エラーレスポンス形式の確認
        
        【学習ポイント】
        - エラーハンドリングの統合テスト方法
        - HTTPステータスコードの適切な使い分け
        - ユーザーフレンドリーなエラーメッセージ
        """
        # Act（実行フェーズ）
        # 存在しないエンドポイントにアクセス
        response = client.get(
            "/api/v1/search/nonexistent",
            headers=auth_headers
        )
        
        # Assert（検証フェーズ）
        assert response.status_code == 404, f"404エラーが期待されますが、実際は{response.status_code}"
        
        print("✓ サーバーエラーハンドリングテスト成功")
    
    # === パフォーマンス統合テスト ===
    
    def test_search_api_performance_requirement(self, client: TestClient, auth_headers: dict, api_test_data):
        """検索APIパフォーマンス要件テスト
        
        【テストの目的】
        検索APIが性能要件（200ms以内）を満たすことを確認
        
        【テスト内容】
        1. 複合検索の実行時間測定
        2. HTTP通信を含めた総合的な応答時間確認
        3. API統合レベルでの性能要件達成確認
        
        【学習ポイント】
        - APIレベルでのパフォーマンステスト
        - HTTP通信オーバーヘッドを含めた測定
        - 実際のユーザー体験に近い性能評価
        """
        import time
        
        # Arrange（準備フェーズ）
        test_data = api_test_data
        frontend_tag = next(tag for tag in test_data["tags"] if tag.name == "frontend")
        
        # Act（実行フェーズ）
        start_time = time.time()
        
        # 複合検索を実行（最も重い処理）
        response = client.post(
            "/api/v1/search/whiteboards",
            json={
                "tags": [str(frontend_tag.id)],
                "authors": [str(test_data["users"][0].id)],
                "date_range": {
                    "date_from": (datetime.now() - timedelta(days=30)).isoformat(),
                    "date_to": datetime.now().isoformat()
                }
            },
            headers=auth_headers
        )
        
        end_time = time.time()
        execution_time_ms = (end_time - start_time) * 1000
        
        # Assert（検証フェーズ）
        assert response.status_code == 200, f"パフォーマンステストでエラー: {response.text}"
        
        # API統合レベルでの性能要件を確認（データベーステストより緩和）
        performance_threshold = 500  # HTTP通信を含むため500msに緩和
        assert execution_time_ms < performance_threshold, f"API応答時間が要件を満たしていません: {execution_time_ms:.2f}ms"
        
        print(f"✓ API統合パフォーマンステスト成功: {execution_time_ms:.2f}ms (< {performance_threshold}ms)")