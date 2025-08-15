# プロジェクト構造

## ディレクトリ構成

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
│   ├── Dockerfile.dev   # 開発用Dockerfile
│   ├── requirements.txt # Python依存関係
│   ├── main.py         # アプリケーションエントリーポイント
│   ├── alembic.ini     # マイグレーション設定
│   ├── alembic/        # マイグレーションファイル
│   ├── tests/          # バックエンドテスト
│   └── app/            # アプリケーションコード
│       ├── core/       # 設定・ユーティリティ
│       ├── api/        # APIエンドポイント
│       ├── models/     # データベースモデル
│       ├── schemas/    # Pydanticスキーマ
│       └── websocket/  # WebSocket処理
├── frontend/             # Vue 3 フロントエンド
│   ├── Dockerfile.dev   # 開発用Dockerfile
│   ├── package.json     # Node.js依存関係
│   ├── vite.config.ts   # Viteビルド設定
│   ├── tsconfig.json    # TypeScript設定
│   ├── tailwind.config.js # Tailwind CSS設定
│   ├── .eslintrc.cjs    # ESLint設定
│   ├── .prettierrc     # Prettier設定
│   └── src/
│       ├── main.ts     # アプリケーションエントリーポイント
│       ├── App.vue     # ルートコンポーネント
│       ├── style.css   # グローバルスタイル
│       ├── components/ # Vueコンポーネント
│       ├── views/      # ページコンポーネント
│       ├── router/     # ルーティング設定
│       ├── stores/     # Pinia状態管理
│       ├── api/        # API通信
│       ├── types/      # TypeScript型定義
│       ├── utils/      # ユーティリティ関数
│       └── composables/ # Vue 3コンポーザブル
├── db/                   # データベース関連
│   └── init/            # 初期化スクリプト
├── docker-compose.yml    # Docker Compose設定
├── .env.example         # 環境変数テンプレート
├── .pylintrc           # Python リンティング設定
├── Makefile            # 開発コマンド
└── CLAUDE.md           # Claude Code仕様駆動開発設定
```

## エントリーポイント

### バックエンド
- **メインアプリケーション**: `backend/main.py`
- **FastAPIアプリ**: `/` (ヘルスチェック), `/health`, `/docs`
- **WebSocket**: `/ws/{whiteboard_id}`, `/ws/test`
- **API**: `/api/v1/*` (api_router経由)

### フロントエンド
- **メインアプリケーション**: `frontend/src/main.ts`
- **ルートコンポーネント**: `frontend/src/App.vue`
- **ルーティング**: `frontend/src/router/index.ts`

## データベース構造
- **開発DB**: `whiteboard_dev` (localhost:5432)
- **テストDB**: `whiteboard_test` (localhost:5433)
- **マイグレーション**: Alembicによる管理
- **管理UI**: pgAdmin (localhost:5050)

## 設定ファイル

### 環境設定
- `.env` - 実際の環境変数 (gitignore)
- `.env.example` - 環境変数テンプレート

### 開発ツール設定
- **Docker**: `docker-compose.yml`, `Dockerfile.dev`
- **Make**: `Makefile` (開発コマンド)
- **Python**: `.pylintrc`, `requirements.txt`
- **Node.js**: `package.json`, 各種設定ファイル