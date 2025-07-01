# オンラインホワイトボードアプリ

Vue 3 + TypeScript + FastAPI で構築されたリアルタイムオンラインホワイトボードアプリケーション

## 🚀 クイックスタート

### 前提条件
- Docker & Docker Compose
- Make（オプション、コマンド簡略化のため）

### セットアップ

1. **リポジトリをクローン**
```bash
git clone <repository-url>
cd 05_whiteBoard
```

2. **環境設定ファイルの準備**
```bash
cp .env.example .env
```

3. **Docker Composeでサービス起動**
```bash
# 全サービスを起動（推奨）
docker-compose up --build -d

# または、フロントエンドとバックエンドのみ
docker-compose up frontend backend --build -d
```

4. **アクセス確認**
- **フロントエンド**: http://localhost:3000/
- **バックエンドAPI**: http://localhost:8000/
- **API文書**: http://localhost:8000/docs

> **⚠️ 起動時の問題**: フロントエンドにアクセスできない場合は [docs/development/docker-setup.md](./docs/development/docker-setup.md) のトラブルシューティングを参照してください。

## 📁 プロジェクト構成

```
.
├── docs/                 # プロジェクトドキュメント
│   ├── README.md        # ドキュメント索引
│   ├── requirements/    # 要件定義
│   ├── design/         # 設計書
│   ├── deployment/     # デプロイ関連
│   ├── development/    # 開発関連
│   └── logs/           # 作業記録
├── backend/              # FastAPI バックエンド
│   ├── Dockerfile.dev
│   ├── requirements.txt
│   ├── main.py
│   └── app/            # アプリケーション構造
├── frontend/             # Vue 3 フロントエンド
│   ├── Dockerfile.dev
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
├── db/                   # データベース関連
│   └── init/
├── docker-compose.yml    # Docker Compose設定
├── .env.example         # 環境変数テンプレート
└── Makefile            # 開発コマンド
```

## 🛠️ 開発コマンド

### Make コマンド（推奨）
```bash
make help           # 利用可能なコマンド一覧
make setup          # 初期セットアップ
make up             # サービス起動
make down           # サービス停止
make logs           # ログ表示
make test           # テスト実行
make lint           # コード品質チェック
make format         # コードフォーマット
make shell-backend  # バックエンドコンテナシェル
make shell-frontend # フロントエンドコンテナシェル

# 作業記録管理
make log-new TASK=task_name  # 新しい作業記録作成
make log-weekly             # 週次まとめ作成
make log-list              # 最近の作業記録一覧
```

### Docker Compose コマンド
```bash
docker-compose up -d              # サービス起動
docker-compose down               # サービス停止
docker-compose logs -f [service]  # ログ表示
docker-compose exec [service] bash # コンテナシェル
```

## 🧪 テスト

### バックエンドテスト
```bash
make test
# または
docker-compose exec backend pytest
```

### フロントエンドテスト
```bash
make test-frontend
# または
docker-compose exec frontend npm test
```

## 📋 開発ガイドライン

### 環境変数
- `.env.example` をコピーして `.env` を作成
- 本番環境では適切な値に変更

### ホットリロード
- フロントエンド: ファイル変更時に自動更新
- バックエンド: ファイル変更時に自動更新

### データベース
- 開発用: PostgreSQL (localhost:5432)
- テスト用: PostgreSQL (localhost:5433)

### コード品質
```bash
make lint    # リンティング
make format  # コードフォーマット
```

## 🔧 トラブルシューティング

### よくある問題

1. **ポートが使用中**
```bash
# ポート使用状況確認
lsof -i :3000
lsof -i :8000
lsof -i :5432
```

2. **Docker容量不足**
```bash
make clean
docker system prune -a
```

3. **データベース接続エラー**
```bash
make logs-db
make reset-db
```

### 開発環境リセット
```bash
make clean
make setup
make up
```

## 📖 技術スタック

- **フロントエンド**: Vue 3, TypeScript, Composition API
- **バックエンド**: FastAPI, Python 3.10
- **データベース**: PostgreSQL 15
- **リアルタイム通信**: WebSocket
- **開発環境**: Docker, Docker Compose

## 📚 ドキュメント

詳細なドキュメントは [docs/](./docs/) ディレクトリを参照してください：

- **要件定義**: [docs/requirements/](./docs/requirements/)
- **設計書**: [docs/design/](./docs/design/)  
- **デプロイ**: [docs/deployment/](./docs/deployment/)
- **開発ガイド**: [docs/development/](./docs/development/)
- **作業記録**: [docs/logs/](./docs/logs/)

## 🤝 開発チーム向け情報

### ブランチ戦略
- `main`: 本番環境
- `develop`: 開発環境
- `feature/*`: 機能開発

### コミット規約
```
feat: 新機能
fix: バグ修正
docs: ドキュメント
style: コードスタイル
refactor: リファクタリング
test: テスト
chore: 雑務
```

### 開発フロー
1. 機能ブランチ作成
2. 開発・テスト
3. プルリクエスト
4. コードレビュー
5. マージ