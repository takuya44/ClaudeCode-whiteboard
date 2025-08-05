# テクノロジースタック

## アーキテクチャ

### システム全体構成
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   フロントエンド  │────▶│   バックエンド   │────▶│  データベース    │
│   Vue 3 + TS    │     │    FastAPI      │     │   PostgreSQL    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │
         └───── WebSocket ───────┘
```

### 通信プロトコル
- **REST API**: 認証、ユーザー管理、ホワイトボード管理
- **WebSocket**: リアルタイム描画同期、ユーザープレゼンス

## フロントエンド

### コアフレームワーク
- **Vue 3** (v3.3.8): プログレッシブJavaScriptフレームワーク
- **TypeScript** (v5.2.0): 型安全性を提供
- **Composition API**: リアクティブで再利用可能なロジック

### 状態管理とルーティング
- **Pinia** (v2.1.7): Vue 3用の状態管理ライブラリ
- **Vue Router** (v4.2.5): シングルページアプリケーションルーティング

### ビルドツールと開発環境
- **Vite** (v5.0.0): 高速なビルドツール
- **Vue TSC**: TypeScriptの型チェック

### UIとスタイリング
- **Tailwind CSS** (v3.3.6): ユーティリティファーストCSSフレームワーク
- **@tailwindcss/forms** (v0.5.7): フォーム要素のスタイリング
- **PostCSS** (v8.4.32): CSSの変換ツール
- **Autoprefixer** (v10.4.16): ベンダープレフィックス自動付与

### HTTPクライアントとユーティリティ
- **Axios** (v1.6.2): HTTPクライアント
- **@vueuse/core** (v10.5.0): Vue Composition API ユーティリティ

### テストツール
- **Vitest** (v1.0.0): 単体テストフレームワーク
- **@vue/test-utils** (v2.4.2): Vueコンポーネントテストユーティリティ
- **Playwright** (v1.40.0): E2Eテストフレームワーク

### コード品質ツール
- **ESLint** (v8.54.0): JavaScriptリンター
- **Prettier** (v3.1.0): コードフォーマッター
- **TypeScript ESLint**: TypeScript用ESLintプラグイン

## バックエンド

### コアフレームワーク
- **Python** (3.10): プログラミング言語
- **FastAPI** (v0.104.1): 高性能Webフレームワーク
- **Uvicorn** (v0.24.0): ASGIサーバー

### データベースとORM
- **PostgreSQL** (15): リレーショナルデータベース
- **SQLAlchemy** (v2.0.23): Python SQL ツールキットとORM
- **Alembic** (v1.12.1): データベースマイグレーションツール
- **psycopg2-binary** (v2.9.9): PostgreSQLアダプター

### WebSocketとリアルタイム通信
- **websockets** (v12.0): WebSocketクライアント/サーバーライブラリ

### データ検証とシリアライゼーション
- **Pydantic** (v2.5.0): データ検証ライブラリ
- **pydantic-settings** (v2.1.0): 設定管理
- **email-validator** (v2.1.0): メールアドレス検証

### 認証とセキュリティ
- **python-jose[cryptography]** (v3.3.0): JWT トークン処理
- **passlib[bcrypt]** (v1.7.4): パスワードハッシュ化
- **python-multipart** (v0.0.6): フォームデータ処理

### テストツール
- **pytest** (v7.4.3): テストフレームワーク
- **pytest-asyncio** (v0.21.1): 非同期テストサポート
- **pytest-cov** (v4.1.0): カバレッジ測定
- **httpx** (v0.25.2): 非同期HTTPクライアント（テスト用）

### コード品質ツール
- **black** (v23.11.0): Pythonコードフォーマッター
- **flake8** (v6.1.0): Pythonリンター
- **isort** (v5.12.0): importソートツール

### 環境管理
- **python-dotenv** (v1.0.0): 環境変数管理

## 開発環境

### コンテナ化
- **Docker**: アプリケーションコンテナ化
- **Docker Compose**: マルチコンテナアプリケーション管理

### データベース管理
- **pgAdmin**: PostgreSQL管理ツール（ポート5050）

### 開発ツール
- **Make**: タスク自動化
- **Git**: バージョン管理

## 共通コマンド

### 開発環境起動
```bash
# Docker Composeで全サービス起動
docker-compose up --build -d

# Makefileを使用
make up
```

### データベースマイグレーション
```bash
# Alembicマイグレーション実行
docker-compose exec backend alembic upgrade head

# Makefileを使用
make migrate
```

### テスト実行
```bash
# バックエンドテスト
make test

# フロントエンドテスト
make test-frontend

# 検索機能テスト
cd backend && pytest tests/test_whiteboard_search.py
```

### コード品質チェック
```bash
# リンティング
make lint

# フォーマット
make format
```

## 環境変数

### フロントエンド
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### バックエンド
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/whiteboard_dev
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### データベース
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=whiteboard_dev
```

## ポート設定

- **フロントエンド**: 3000
- **バックエンドAPI**: 8000
- **PostgreSQL（開発）**: 5432
- **PostgreSQL（テスト）**: 5433
- **pgAdmin**: 5050

## デプロイメント考慮事項

### スケーラビリティ
- WebSocketサーバーの水平スケーリング対応設計
- Redis導入によるセッション管理（将来実装）

### クラウドプロバイダー対応
- AWS、GCP、Azure対応可能なコンテナベースアーキテクチャ
- 環境変数による設定の外部化

### CI/CD
- GitHub Actions対応（将来実装予定）
- Docker イメージのビルドとプッシュ自動化