# 技術スタック

## フロントエンド
- **フレームワーク**: Vue 3.3.8 (Composition API)
- **言語**: TypeScript 5.2.0
- **ビルドツール**: Vite 5.0.0
- **状態管理**: Pinia 2.1.7
- **ルーティング**: Vue Router 4.2.5
- **スタイリング**: Tailwind CSS 3.3.6
- **HTTP クライアント**: Axios 1.6.2
- **ユーティリティ**: @vueuse/core 10.5.0

### フロントエンド開発依存関係
- **テスト**: Vitest 1.0.0, @vue/test-utils 2.4.2, @playwright/test 1.40.0
- **リンティング**: ESLint 8.54.0 with Vue 3 configuration
- **フォーマッティング**: Prettier 3.1.0
- **型チェック**: vue-tsc 1.8.22

## バックエンド
- **フレームワーク**: FastAPI 0.104.1
- **言語**: Python 3.10
- **ASGIサーバー**: uvicorn 0.24.0
- **ORM**: SQLAlchemy 2.0.23
- **マイグレーション**: Alembic 1.12.1
- **データベースドライバー**: psycopg2-binary 2.9.9
- **WebSocket**: websockets 12.0
- **バリデーション**: Pydantic 2.5.0
- **認証**: python-jose, passlib
- **環境変数**: python-dotenv 1.0.0

### バックエンド開発依存関係
- **テスト**: pytest 7.4.3, pytest-asyncio 0.21.1, httpx 0.25.2
- **コード品質**: black 23.11.0, flake8 6.1.0, isort 5.12.0

## データベース
- **DB**: PostgreSQL 15
- **管理ツール**: pgAdmin4 (localhost:5050)
- **開発DB**: whiteboard_dev (localhost:5432)
- **テストDB**: whiteboard_test (localhost:5433)

## 開発ツール
- **コンテナ**: Docker + Docker Compose
- **ビルドオートメーション**: Make
- **プロジェクト管理**: npm scripts (フロントエンド)