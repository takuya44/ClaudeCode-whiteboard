## 調査タスク：Whiteboard アプリケーション API 調査

**対象**

- Whiteboard アプリケーションの Backend API (FastAPI)
- Frontend (Vue.js) から Backend API への連携
- WebSocket による リアルタイム通信

**調査項目**

### 1. Backend API エンドポイント調査
- 認証 API (`/api/v1/auth/*`)
  - ユーザー登録、ログイン、プロフィール管理
- Whiteboard API (`/api/v1/whiteboards/*`)
  - ホワイトボードの CRUD 操作
  - 共有・権限管理
- Drawing Elements API (`/api/v1/whiteboards/{id}/elements/*`)
  - 描画要素の CRUD 操作
- WebSocket エンドポイント (`/ws/*`)
  - リアルタイム協調編集

### 2. Frontend から Backend API の呼び出し箇所
- `frontend/src/api/` 内の API クライアント実装
- `frontend/src/stores/` 内の状態管理での API 呼び出し
- `frontend/src/views/` 内のコンポーネントからの API 利用

### 3. 認証・セキュリティ
- JWT トークンベース認証の実装
- OAuth2 with Password Flow
- API キーやトークンの管理方法
- CORS 設定

### 4. エラーハンドリング
- Backend でのエラーレスポンス形式
- Frontend でのエラー処理実装
- WebSocket 接続エラーの処理

### 5. リアルタイム通信
- WebSocket 接続の確立方法
- メッセージフォーマット
- 描画データの同期プロトコル

**成果物**  
`.claude/tmp/api_integration_report.md` に以下の形式でまとめる：
- API エンドポイント一覧（RESTful API + WebSocket）
- 認証フロー図
- エラーハンドリングのパターン
- WebSocket 通信プロトコル仕様

**プロンプト使用例**

```bash
# このプロンプトを使用して API 連携を調査
# 1. Backend の API 定義を確認
#    - backend/app/api/v1/ 配下のルーター定義
#    - backend/app/main.py の API マウント箇所
# 2. Frontend の API クライアント実装を確認
#    - frontend/src/api/ 配下の実装
# 3. 調査結果を .claude/tmp/api_integration_report.md に記載
```
