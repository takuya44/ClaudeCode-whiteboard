# 開発環境セットアップガイド

## 🚀 クイックスタート

### 前提条件
- Docker Desktop
- Git
- Make（推奨）

### 1. リポジトリセットアップ
```bash
git clone <repository-url>
cd whiteboard-app
```

### 2. 初期セットアップ
```bash
make setup
```

### 3. 開発サーバー起動
```bash
make up
```

### 4. 動作確認
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000/docs

## 📋 詳細セットアップ手順

### Docker環境セットアップ

1. **環境変数設定**
```bash
cp .env.example .env
# .env ファイルを編集（通常はデフォルトのままでOK）
```

2. **コンテナビルド**
```bash
docker-compose build
```

3. **サービス起動**
```bash
docker-compose up -d
```

### 開発ツール設定

#### VS Code推奨拡張機能
```json
{
  "recommendations": [
    "ms-python.python",
    "vue.volar",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode-remote.remote-containers",
    "bradlc.vscode-tailwindcss"
  ]
}
```

#### エディタ設定
```json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "typescript.preferences.importModuleSpecifier": "relative",
  "vue.server.hybridMode": true
}
```

## 🛠️ 開発コマンド

### Make コマンド
```bash
make help           # コマンド一覧
make setup          # 初期セットアップ
make up             # サービス起動
make down           # サービス停止
make logs           # ログ表示
make test           # テスト実行
make shell-backend  # バックエンドシェル
make shell-frontend # フロントエンドシェル
```

### Docker Compose コマンド
```bash
# サービス管理
docker-compose up -d
docker-compose down
docker-compose restart [service]

# ログ確認
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# コンテナシェル
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🧪 テスト環境

### バックエンドテスト
```bash
# テスト実行
make test
docker-compose exec backend pytest

# カバレッジ付きテスト
docker-compose exec backend pytest --cov=.

# 特定テスト実行
docker-compose exec backend pytest tests/test_websocket.py
```

### フロントエンドテスト
```bash
# テスト実行
make test-frontend
docker-compose exec frontend npm test

# E2Eテスト
docker-compose exec frontend npm run test:e2e
```

## 🔧 トラブルシューティング

### よくある問題

#### 1. フロントエンドにアクセスできない 🔥
**最も多い問題**: コンテナは起動しているが、ブラウザからアクセスできない

```bash
# 症状確認
curl -I http://localhost:3000/
# → Connection reset by peer

# 解決方法: Vite設定を確認
# frontend/vite.config.ts で host: '0.0.0.0' になっているか確認
```

**詳細な解決手順**: [docker-setup.md](./docker-setup.md#1-フロントエンドにブラウザからアクセスできない) を参照

#### 2. ポート競合エラー
```bash
# 使用中ポート確認
lsof -i :3000
lsof -i :8000
lsof -i :5432

# 該当プロセス終了
kill -9 <PID>
```

#### 3. Python依存関係エラー（python-cors問題）
```bash
# 症状: python-cors==1.0.1 のインストールエラー
# 解決: requirements.txt から該当行を削除またはコメントアウト
```

#### 4. Docker容量不足
```bash
# 不要なコンテナ・イメージ削除
docker system prune -a

# ボリューム削除
docker volume prune
```

#### 5. データベース接続エラー
```bash
# データベースログ確認
docker-compose logs db

# データベースリセット
docker-compose down -v
docker-compose up db -d
```

#### 6. Node.js依存関係エラー
```bash
# node_modules再インストール
docker-compose exec frontend rm -rf node_modules
docker-compose exec frontend npm install
```

### 環境リセット
```bash
# 完全リセット
make clean
make setup
make up
```

## 🌐 ブラウザ設定

### 開発者ツール設定
- **Vue Devtools**: Vue 3対応版をインストール
- **WebSocket**: ネットワークタブでWebSocket通信確認

### CORS設定
開発環境では以下のオリジンが許可されています：
- http://localhost:3000
- http://127.0.0.1:3000

## 📱 デバッグ方法

### バックエンドデバッグ
```python
# FastAPIでのデバッグ
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```

### フロントエンドデバッグ
```javascript
// Vue Devtoolsでのデバッグ
console.log('Debug info:', data)
debugger; // ブレークポイント
```

### WebSocketデバッグ
```javascript
// WebSocket接続確認
const ws = new WebSocket('ws://localhost:8000/ws')
ws.onopen = () => console.log('Connected')
ws.onmessage = (event) => console.log('Received:', event.data)
```

## 🔄 ホットリロード

### フロントエンド
- ファイル変更 → 自動更新
- 設定ファイル: `vite.config.ts`

### バックエンド
- ファイル変更 → 自動再起動
- 設定: `uvicorn --reload`

## 📊 パフォーマンス監視

### 開発環境での監視
```bash
# リソース使用量確認
docker stats

# ログ監視
docker-compose logs -f --tail=100
```

## 🔐 環境変数管理

### 開発環境
```bash
# .env ファイル（Git管理対象外）
DATABASE_URL=postgresql://postgres:postgres@db:5432/whiteboard_dev
SECRET_KEY=development-secret-key
DEBUG=True
```

### 本番環境
```bash
# 本番環境では環境変数で設定
export DATABASE_URL="postgresql://..."
export SECRET_KEY="production-secret"
export DEBUG=False
```