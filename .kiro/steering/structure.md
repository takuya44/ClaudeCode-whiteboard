# プロジェクト構造

## ルートディレクトリ構成

```
05_whiteBoard/
├── frontend/              # Vue 3 フロントエンドアプリケーション
├── backend/               # FastAPI バックエンドアプリケーション
├── db/                    # データベース初期化スクリプト
├── docs/                  # プロジェクトドキュメント
├── .kiro/                 # Kiro仕様駆動開発関連
│   ├── steering/         # プロジェクトステアリング文書
│   └── specs/            # 機能仕様書
├── .claude/               # Claude Code設定とコマンド
├── docker-compose.yml     # Docker Compose設定
├── Makefile              # 開発タスク自動化
├── .env.example          # 環境変数テンプレート
├── README.md             # プロジェクト概要
└── CLAUDE.md             # Claude Code用プロジェクト仕様
```

## サブディレクトリ構造

### フロントエンド構造 (`frontend/`)

```
frontend/
├── src/
│   ├── api/              # APIクライアントモジュール
│   │   ├── auth.ts       # 認証関連API
│   │   ├── whiteboard.ts # ホワイトボード関連API
│   │   └── index.ts      # APIクライアント設定
│   ├── components/       # Vueコンポーネント
│   │   ├── common/       # 共通UIコンポーネント
│   │   ├── ui/           # 基本UIコンポーネント
│   │   └── whiteboard/   # ホワイトボード専用コンポーネント
│   ├── composables/      # Vue Composition API カスタムフック
│   ├── layouts/          # ページレイアウトコンポーネント
│   ├── router/           # Vue Routerルーティング設定
│   ├── stores/           # Pinia状態管理ストア
│   │   ├── auth.ts       # 認証状態管理
│   │   ├── whiteboard.ts # ホワイトボード状態管理
│   │   └── search.ts     # 検索状態管理（新機能）
│   ├── types/            # TypeScript型定義
│   │   ├── index.ts      # 基本型定義
│   │   └── search.ts     # 検索関連型定義（新機能）
│   ├── utils/            # ユーティリティ関数
│   ├── views/            # ページコンポーネント
│   │   └── auth/         # 認証関連ページ
│   ├── App.vue           # ルートコンポーネント
│   ├── main.ts           # アプリケーションエントリーポイント
│   └── style.css         # グローバルスタイル
├── public/               # 静的アセット
├── dist/                 # ビルド出力ディレクトリ
├── node_modules/         # npmパッケージ
├── package.json          # npm設定
├── tsconfig.json         # TypeScript設定
├── vite.config.ts        # Viteビルド設定
└── tailwind.config.js    # Tailwind CSS設定
```

### バックエンド構造 (`backend/`)

```
backend/
├── app/
│   ├── api/              # APIエンドポイント
│   │   └── v1/           # APIバージョン1
│   │       ├── auth.py   # 認証エンドポイント
│   │       ├── whiteboards.py # ホワイトボードエンドポイント
│   │       ├── elements.py    # 描画要素エンドポイント
│   │       ├── search.py      # 検索エンドポイント（新機能）
│   │       └── api.py    # APIルーター統合
│   ├── core/             # コア機能
│   │   ├── config.py     # アプリケーション設定
│   │   ├── database.py   # データベース接続
│   │   ├── dependencies.py # FastAPI依存性注入
│   │   └── security.py   # セキュリティ関連
│   ├── models/           # SQLAlchemyモデル
│   │   ├── user.py       # ユーザーモデル
│   │   ├── whiteboard.py # ホワイトボードモデル
│   │   ├── collaborator.py # コラボレーターモデル
│   │   ├── tag.py        # タグモデル（新機能）
│   │   └── whiteboard_tag.py # ホワイトボード-タグ関連モデル（新機能）
│   ├── schemas/          # Pydanticスキーマ
│   │   ├── auth.py       # 認証スキーマ
│   │   ├── user.py       # ユーザースキーマ
│   │   ├── whiteboard.py # ホワイトボードスキーマ
│   │   ├── element.py    # 描画要素スキーマ
│   │   └── search.py     # 検索関連スキーマ（新機能）
│   ├── websocket/        # WebSocket関連
│   │   ├── connection_manager.py # 接続管理
│   │   ├── message_handler.py    # メッセージ処理
│   │   └── websocket.py  # WebSocketエンドポイント
│   ├── services/         # ビジネスロジック層
│   │   └── search_service.py # 検索サービス（新機能）
│   ├── repositories/     # データアクセス層（リポジトリパターン）
│   │   └── whiteboard_repository.py # ホワイトボードリポジトリ
│   └── utils/            # ユーティリティ関数
├── alembic/              # データベースマイグレーション
├── tests/                # テストファイル
│   ├── services/         # サービステスト
│   │   └── test_search_service.py # 検索サービステスト（新機能）
│   ├── conftest.py       # テスト設定
│   └── test_whiteboard_search.py # 検索機能テスト（新機能）
├── main.py               # FastAPIアプリケーションエントリーポイント
├── requirements.txt      # Python依存関係
└── Dockerfile.dev        # 開発用Dockerfile
```

### ドキュメント構造 (`docs/`)

```
docs/
├── requirements/         # 要件定義書
├── development/          # 開発ガイド
├── deployment/           # デプロイメントガイド
├── review/              # コードレビュー記録
├── 日報/                # 開発進捗記録
└── プロジェクトドキュメント/  # 詳細設計書
```

## コード構成パターン

### フロントエンド

#### コンポーネント構成
- **単一ファイルコンポーネント**: `.vue`拡張子でテンプレート、スクリプト、スタイルを統合
- **Composition API**: `<script setup>`構文を使用
- **TypeScript**: すべてのコンポーネントで型定義を使用

#### 状態管理
- **Piniaストア**: 機能ごとに分離（auth、whiteboard）
- **リアクティブ状態**: `ref`、`reactive`、`computed`を活用
- **永続化**: 必要に応じてlocalStorageと同期

#### API通信
- **Axiosインスタンス**: 共通設定とインターセプター
- **型安全**: APIレスポンスの型定義
- **エラーハンドリング**: 統一されたエラー処理

### バックエンド

#### APIレイヤー構成
- **FastAPIルーター**: 機能別にルーターを分離
- **依存性注入**: データベースセッションと認証の注入
- **バージョニング**: `/api/v1`プレフィックス

#### データレイヤー
- **SQLAlchemyモデル**: テーブル定義とリレーション
- **リポジトリパターン**: データアクセスロジックの抽象化
- **Pydanticスキーマ**: リクエスト/レスポンスの検証
- **マイグレーション**: Alembicによるスキーマ管理

#### WebSocket
- **ConnectionManager**: 接続プールの管理
- **メッセージハンドラー**: イベントタイプ別の処理
- **ブロードキャスト**: ルーム単位のメッセージ配信

## ファイル命名規則

### フロントエンド
- **コンポーネント**: PascalCase（例: `WhiteboardCanvas.vue`）
- **composables**: camelCaseで`use`プレフィックス（例: `useCanvas.ts`）
- **ストア**: camelCase（例: `whiteboard.ts`）
- **ビュー**: PascalCaseで`View`サフィックス（例: `DashboardView.vue`）

### バックエンド
- **モジュール**: snake_case（例: `connection_manager.py`）
- **クラス**: PascalCase（例: `WhiteboardModel`）
- **関数**: snake_case（例: `get_current_user`）
- **定数**: UPPER_SNAKE_CASE（例: `SECRET_KEY`）

## インポート構成

### フロントエンド
```typescript
// 外部ライブラリ
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

// 内部モジュール
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/ui/BaseButton.vue'

// 型定義
import type { User } from '@/types'
```

### バックエンド
```python
# 標準ライブラリ
from typing import List, Optional

# サードパーティ
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 内部モジュール
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
```

## 主要アーキテクチャ原則

### 1. レイヤードアーキテクチャ
- **プレゼンテーション層**: Vue コンポーネント
- **ビジネスロジック層**: Piniaストア、FastAPIサービス
- **データアクセス層**: リポジトリパターン、SQLAlchemyモデル

### 2. 関心の分離
- UIロジックとビジネスロジックの分離
- APIクライアントとコンポーネントの分離
- WebSocketとREST APIの責務分離

### 3. 型安全性
- TypeScriptによるフロントエンドの型チェック
- Pydanticによるバックエンドの検証
- API通信の型定義共有

### 4. リアクティブ設計
- Vue 3のリアクティビティシステム活用
- WebSocketによるリアルタイム更新
- 楽観的UI更新パターン

### 5. テスタビリティ
- 依存性注入によるモックの容易性
- 単一責任の原則に基づく設計
- E2Eテストとユニットテストのサポート