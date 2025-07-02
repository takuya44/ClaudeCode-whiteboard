# 🚀 実装者向けハンドオーバープロンプト

**作成日**: 2025年7月1日  
**対象**: バックエンド担当者A・B  
**フェーズ**: Phase 2 基盤実装 → Phase 3 コア機能実装  

---

## 📋 現在の進捗状況

### ✅ **完了済み**
**フロントエンド担当者A・B**: UI/UX基盤 + Canvas描画システム
- プロジェクト基盤設定（Vite + Vue 3 + TypeScript）
- 共通UIコンポーネントシステム
- 状態管理（Pinia）・ルーティング・レイアウト
- Canvas描画エンジン（useCanvas composable）
- WebSocket通信システム（useWebSocket composable）
- 描画ツールUI（ペン、線、図形、色選択等）
- リアルタイム同期準備完了

### ⏳ **次の実装対象**
**あなたの担当**: バックエンドAPI・データベース・WebSocketサーバー

---

## 🎯 バックエンド担当者A向けプロンプト

### 実装タスク概要
```
オンラインホワイトボードアプリのバックエンドAPI・データベース・認証システムを実装してください。

【プロジェクト概要】
- Vue 3 + FastAPI によるリアルタイム描画アプリ
- フロントエンド側の準備完了済み
- API設計・データベース設計・認証システムの実装が必要

【技術スタック】
- FastAPI (Python)
- PostgreSQL + SQLAlchemy + Alembic
- JWT認証
- Docker環境
```

### 🔧 開発環境セットアップ
```bash
# プロジェクトルートに移動
cd /Users/takunari/Desktop/workspace/08_claudeCode/05_whiteBoard

# Docker環境起動（データベース・バックエンド）
docker-compose up -d db backend

# バックエンドコンテナに接続
docker-compose exec backend bash

# 依存関係確認
pip list

# データベース接続確認
python -c "from app.database import engine; print('DB Connected')"
```

### 📊 実装すべきAPIエンドポイント

#### 認証系API
```python
# ユーザー認証・管理
POST   /api/auth/register        # ユーザー登録
POST   /api/auth/login           # ログイン
POST   /api/auth/logout          # ログアウト
GET    /api/auth/me              # 現在のユーザー情報
PUT    /api/auth/profile         # プロフィール更新
```

#### ホワイトボード管理API
```python
# ホワイトボード CRUD
GET    /api/whiteboards          # ホワイトボード一覧
POST   /api/whiteboards          # ホワイトボード作成
GET    /api/whiteboards/{id}     # ホワイトボード詳細
PUT    /api/whiteboards/{id}     # ホワイトボード更新
DELETE /api/whiteboards/{id}     # ホワイトボード削除

# 共有・権限管理
POST   /api/whiteboards/{id}/share    # ホワイトボード共有
GET    /api/whiteboards/{id}/users    # 参加ユーザー一覧
PUT    /api/whiteboards/{id}/permissions  # 権限変更
```

#### 描画要素管理API
```python
# 描画要素 CRUD
GET    /api/whiteboards/{id}/elements     # 描画要素一覧
POST   /api/whiteboards/{id}/elements     # 描画要素作成
PUT    /api/whiteboards/{id}/elements/{element_id}  # 描画要素更新
DELETE /api/whiteboards/{id}/elements/{element_id}  # 描画要素削除
```

### 🗄️ データベース設計

#### 必要なテーブル
```sql
-- ユーザーテーブル
users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    avatar VARCHAR,
    role VARCHAR DEFAULT 'user',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- ホワイトボードテーブル
whiteboards (
    id UUID PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- 描画要素テーブル
drawing_elements (
    id UUID PRIMARY KEY,
    whiteboard_id UUID REFERENCES whiteboards(id),
    type VARCHAR NOT NULL, -- 'pen', 'line', 'rectangle', 'circle', 'text'
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    width FLOAT,
    height FLOAT,
    end_x FLOAT,
    end_y FLOAT,
    points JSONB, -- ペンストローク用
    color VARCHAR NOT NULL,
    stroke_width INTEGER,
    fill_color VARCHAR,
    text_content TEXT,
    font_size INTEGER,
    font_family VARCHAR,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- ホワイトボード参加者テーブル
whiteboard_collaborators (
    id UUID PRIMARY KEY,
    whiteboard_id UUID REFERENCES whiteboards(id),
    user_id UUID REFERENCES users(id),
    permission VARCHAR DEFAULT 'edit', -- 'view', 'edit', 'admin'
    joined_at TIMESTAMP,
    UNIQUE(whiteboard_id, user_id)
)
```

### 💾 フロントエンド連携用の型定義

#### API レスポンス形式
```python
# フロントエンドの型定義と合わせる
# /frontend/src/types/index.ts を参照

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar: Optional[str]
    role: str
    created_at: datetime
    updated_at: datetime

class WhiteboardResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    owner_id: str
    is_public: bool
    created_at: datetime
    updated_at: datetime
    collaborators: List[UserResponse]

class DrawingElementResponse(BaseModel):
    id: str
    whiteboard_id: str
    type: str  # 'pen' | 'line' | 'rectangle' | 'circle' | 'text' | 'sticky'
    x: float
    y: float
    width: Optional[float]
    height: Optional[float]
    end_x: Optional[float]
    end_y: Optional[float]
    points: Optional[List[Dict[str, float]]]  # [{"x": 10, "y": 20}, ...]
    color: str
    stroke_width: Optional[int]
    fill: Optional[str]
    text: Optional[str]
    font_size: Optional[int]
    font_family: Optional[str]
    user_id: str
    created_at: datetime
    updated_at: datetime
```

### 🔧 実装開始手順

1. **Alembicマイグレーション作成**
```bash
# マイグレーションファイル作成
alembic revision --autogenerate -m "Create initial tables"

# マイグレーション実行
alembic upgrade head
```

2. **モデル実装** (`app/models/`)
   - `user.py` - Userモデル
   - `whiteboard.py` - Whiteboard, DrawingElementモデル
   - `collaborator.py` - Collaboratorモデル

3. **スキーマ実装** (`app/schemas/`)
   - Pydanticスキーマでリクエスト・レスポンス定義

4. **API実装** (`app/api/`)
   - `auth.py` - 認証エンドポイント
   - `whiteboards.py` - ホワイトボード管理
   - `elements.py` - 描画要素管理

5. **フロントエンド連携テスト**
```bash
# フロントエンド起動（別ターミナル）
docker-compose up -d frontend

# APIテスト
curl -X GET http://localhost:8000/api/whiteboards
```

---

## 🎯 バックエンド担当者B向けプロンプト

### 実装タスク概要
```
オンラインホワイトボードアプリのWebSocketサーバー・リアルタイム通信システムを実装してください。

【プロジェクト概要】
- Vue 3フロントエンドからのWebSocket接続受信
- リアルタイム描画データの配信・同期
- マルチユーザーセッション管理

【技術スタック】
- FastAPI WebSocket
- Redis（セッション管理・メッセージブローカー）
- 非同期処理（asyncio）
```

### 🔧 開発環境セットアップ
```bash
# Redis起動（docker-compose.ymlに追加要）
docker-compose up -d redis

# WebSocketサーバー起動確認
# フロントエンドからの接続テスト用URL
ws://localhost:8000/ws/{whiteboard_id}?userId={user_id}
```

### 📡 WebSocketメッセージ仕様

#### フロントエンド → バックエンド
```typescript
// フロントエンド側の型定義（参考）
// /frontend/src/types/index.ts
interface WebSocketMessage {
  type: 'draw' | 'erase' | 'cursor' | 'user_join' | 'user_leave' | 'ping' | 'drawing_event'
  data: any
  userId: string
  timestamp: string
}

// 描画更新メッセージ
{
  type: 'draw',
  data: {
    element: DrawingElement // 新しい描画要素
  },
  userId: 'user123',
  timestamp: '2025-07-01T12:00:00Z'
}

// カーソル位置更新
{
  type: 'cursor',
  data: { x: 100, y: 200 },
  userId: 'user123',
  timestamp: '2025-07-01T12:00:00Z'
}

// ユーザー参加・離脱
{
  type: 'user_join',
  data: { userId: 'user123', userName: 'Alice' },
  userId: 'user123',
  timestamp: '2025-07-01T12:00:00Z'
}
```

### 🏗️ WebSocketサーバー実装構造

#### 必要なクラス・機能
```python
# app/websocket/connection_manager.py
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_sessions: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, whiteboard_id: str, user_id: str)
    async def disconnect(self, websocket: WebSocket, whiteboard_id: str, user_id: str)
    async def broadcast_to_whiteboard(self, whiteboard_id: str, message: dict, exclude_user: str = None)
    async def send_to_user(self, user_id: str, message: dict)

# app/websocket/message_handler.py
class MessageHandler:
    async def handle_drawing_update(self, message: dict, whiteboard_id: str, user_id: str)
    async def handle_cursor_update(self, message: dict, whiteboard_id: str, user_id: str)
    async def handle_user_join(self, message: dict, whiteboard_id: str, user_id: str)
    async def handle_user_leave(self, message: dict, whiteboard_id: str, user_id: str)

# app/websocket/session_manager.py
class SessionManager:
    """Redis を使用したセッション管理"""
    async def add_user_to_whiteboard(self, whiteboard_id: str, user_id: str, user_info: dict)
    async def remove_user_from_whiteboard(self, whiteboard_id: str, user_id: str)
    async def get_whiteboard_users(self, whiteboard_id: str) -> List[dict]
    async def store_drawing_element(self, whiteboard_id: str, element: dict)
```

### 🔄 リアルタイム同期フロー

#### 描画同期プロセス
```python
# WebSocketエンドポイント実装例
@app.websocket("/ws/{whiteboard_id}")
async def websocket_endpoint(websocket: WebSocket, whiteboard_id: str, userId: str):
    await connection_manager.connect(websocket, whiteboard_id, userId)
    try:
        while True:
            # フロントエンドからのメッセージ受信
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # メッセージタイプ別処理
            if message['type'] == 'draw':
                # 描画要素をデータベースに保存
                await save_drawing_element(message['data']['element'])
                # 他のユーザーにブロードキャスト
                await connection_manager.broadcast_to_whiteboard(
                    whiteboard_id, message, exclude_user=userId
                )
            
            elif message['type'] == 'cursor':
                # カーソー位置のリアルタイム配信（保存しない）
                await connection_manager.broadcast_to_whiteboard(
                    whiteboard_id, message, exclude_user=userId
                )
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket, whiteboard_id, userId)
```

### 📊 パフォーマンス最適化

#### 必要な実装項目
```python
# メッセージスロットリング
class MessageThrottler:
    """高頻度メッセージの間引き処理"""
    async def throttle_cursor_updates(self, user_id: str, message: dict) -> bool
    async def throttle_drawing_updates(self, user_id: str, message: dict) -> bool

# データ圧縮
class MessageCompressor:
    """WebSocketメッセージの圧縮・展開"""
    def compress_drawing_data(self, element: dict) -> dict
    def decompress_drawing_data(self, compressed: dict) -> dict

# セッション永続化
class SessionPersistence:
    """ユーザーセッションの永続化"""
    async def save_session_state(self, whiteboard_id: str, session_data: dict)
    async def restore_session_state(self, whiteboard_id: str) -> dict
```

### 🧪 WebSocket テスト方法

#### フロントエンド連携テスト
```bash
# 1. フロントエンド起動
docker-compose up -d frontend

# 2. ブラウザでアクセス
open http://localhost:3000

# 3. ホワイトボードページで描画テスト
# WebSocketコンソールで接続状況確認

# 4. 複数ブラウザで同時描画テスト
# 別ブラウザ・シークレットモードで同じホワイトボードにアクセス
```

---

## 📁 プロジェクト構造（参考）

```
📦 05_whiteBoard/
├── 📁 frontend/                    ✅ 実装完了
│   ├── src/components/whiteboard/  ✅ Canvas描画システム
│   ├── src/composables/            ✅ useCanvas, useWebSocket
│   └── src/types/index.ts          ✅ TypeScript型定義
├── 📁 backend/                     🔄 あなたの実装対象
│   ├── app/
│   │   ├── api/                    📝 REST API実装
│   │   ├── models/                 📝 データベースモデル
│   │   ├── schemas/                📝 Pydanticスキーマ
│   │   ├── websocket/              📝 WebSocket処理
│   │   ├── core/                   📝 認証・設定
│   │   └── services/               📝 ビジネスロジック
│   ├── alembic/                    📝 マイグレーション
│   └── tests/                      📝 テスト
└── 📁 docs/                        📚 設計書・ログ
    ├── development/                ✅ 実装計画書
    └── logs/                       ✅ 実装ログ
```

---

## 🔗 重要な参考資料

### フロントエンド実装済み機能
- **描画エンジン**: `/frontend/src/composables/useCanvas.ts`
- **WebSocket通信**: `/frontend/src/composables/useWebSocket.ts`
- **型定義**: `/frontend/src/types/index.ts`
- **UI コンポーネント**: `/frontend/src/components/whiteboard/`

### 設計書・計画書
- **実装計画書**: `/docs/development/implementation-plan.md`
- **進捗サマリー**: `/docs/development/progress-summary.md`
- **フロントエンド実装ログ**: `/docs/logs/2025-07-01_frontend-developer-*-implementation.md`

### 開発環境・設定
- **Docker設定**: `/docker-compose.yml`
- **フロントエンド設定**: `/frontend/package.json`, `/frontend/vite.config.ts`

---

## 🚨 重要な注意事項

### セキュリティ
- **JWT認証**: 適切なトークン検証・有効期限管理
- **WebSocket認証**: 接続時のユーザー認証必須
- **SQL インジェクション**: SQLAlchemy のORM使用推奨
- **CORS設定**: フロントエンド（localhost:3000）からのアクセス許可

### パフォーマンス
- **WebSocket接続数**: 同時接続数の制限・監視
- **データベース**: インデックス設定・クエリ最適化
- **メッセージ配信**: 不要な配信の削減・効率化

### フロントエンド連携
- **API形式**: フロントエンドの型定義と一致させる
- **WebSocketメッセージ**: フロントエンドの期待する形式で送信
- **エラーハンドリング**: 適切なHTTPステータス・エラーメッセージ

---

## 🎯 成功の指標

### 完了基準
- [ ] フロントエンドからのAPI呼び出しが正常動作
- [ ] WebSocket接続・メッセージ送受信が正常動作
- [ ] 複数ユーザーでの同時描画・リアルタイム同期
- [ ] データベースへの描画データ永続化
- [ ] 認証機能（ログイン・ユーザー管理）動作

### テスト項目
```bash
# API テスト
curl -X POST http://localhost:8000/api/auth/register -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
curl -X GET http://localhost:8000/api/whiteboards

# フロントエンド統合テスト
# http://localhost:3000 でホワイトボード作成・描画・共有ができる

# WebSocket テスト
# 複数ブラウザで同時描画してリアルタイム同期確認
```

---

**実装頑張ってください！フロントエンド側は準備万端です！🚀**

**質問・相談があればいつでもお聞きください。**