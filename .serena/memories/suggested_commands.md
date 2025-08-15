# 推奨開発コマンド

## Make コマンド（推奨）

### 基本操作
- `make help` - 利用可能なコマンド一覧
- `make setup` - 初期セットアップ (.env作成 + ビルド)
- `make up` - 全サービス起動
- `make down` - 全サービス停止
- `make build` - 全コンテナビルド
- `make clean` - サービス停止 + ボリューム削除
- `make logs` - 全ログ表示

### 開発・デバッグ
- `make logs-backend` - バックエンドログ
- `make logs-frontend` - フロントエンドログ  
- `make logs-db` - データベースログ
- `make shell-backend` - バックエンドコンテナシェル
- `make shell-frontend` - フロントエンドコンテナシェル
- `make shell-db` - PostgreSQLシェル

### データベース
- `make migrate` - マイグレーション実行 (重要: 初回必須)
- `make migrate-create name=migration_name` - 新規マイグレーション作成
- `make reset-db` - データベースリセット (注意: 全データ削除)

### テスト・品質
- `make test` - バックエンドテスト実行
- `make test-frontend` - フロントエンドテスト実行
- `make lint` - 全コードリンティング
- `make format` - 全コードフォーマット

### 作業記録管理
- `make log-new TASK=task_name` - 作業記録作成
- `make log-weekly` - 週次まとめ作成
- `make log-list` - 最近の作業記録一覧

## Docker Compose直接コマンド

### 基本操作
- `docker-compose up -d` - バックグラウンド起動
- `docker-compose down` - サービス停止
- `docker-compose logs -f [service]` - ログ表示
- `docker-compose exec [service] bash` - コンテナシェル

### 特定サービス操作
- `docker-compose up frontend backend --build -d` - フロントエンド・バックエンドのみ起動
- `docker-compose restart [service]` - 特定サービス再起動

## NPM コマンド (フロントエンド)

### 開発
- `npm run dev` - 開発サーバー起動
- `npm run build` - プロダクションビルド
- `npm run preview` - ビルド結果プレビュー

### テスト・品質
- `npm test` - 単体テスト実行
- `npm run test:e2e` - E2Eテスト実行  
- `npm run lint` - ESLint実行
- `npm run format` - Prettier実行
- `npm run type-check` - TypeScript型チェック

## Python コマンド (バックエンド)

### テスト・品質
- `pytest` - テスト実行
- `black .` - コードフォーマット
- `flake8 .` - リンティング
- `isort .` - インポート整理

### データベース
- `alembic upgrade head` - マイグレーション適用
- `alembic revision --autogenerate -m "message"` - マイグレーション生成

## システムコマンド (macOS)

### ポート確認
- `lsof -i :3000` - フロントエンドポート確認
- `lsof -i :8000` - バックエンドポート確認
- `lsof -i :5432` - データベースポート確認

### Docker管理
- `docker system prune -a` - 未使用リソース削除
- `docker-compose down -v` - ボリューム含む完全停止