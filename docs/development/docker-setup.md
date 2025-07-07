# Docker環境セットアップ手順書

## 📋 前提条件

- Docker Desktop がインストールされていること
- Docker Compose が利用可能であること（Docker Desktop に含まれています）

## 🚀 クイックスタート

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd 05_whiteBoard
```

### 2. 環境設定ファイルの準備
```bash
# .env ファイルを作成
cp .env.example .env
```

### 3. Docker Composeでサービス起動
```bash
# 全サービスを起動（初回はビルドも実行）
docker-compose up --build -d

# または、フロントエンドとバックエンドのみ起動
docker-compose up frontend backend --build -d
```

### 4. 動作確認
- **フロントエンド**: http://localhost:3000/
- **バックエンド**: http://localhost:8000/
- **API ドキュメント**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050/ (admin@example.com / admin)

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. フロントエンドにブラウザからアクセスできない

**症状**: コンテナは起動しているが、ブラウザで http://localhost:3000/ にアクセスできない

**原因**: Viteの設定でホストが `localhost` になっているため、Dockerコンテナ外部からアクセスできない

**解決方法**:
```bash
# frontend/vite.config.ts を確認・修正
# server.host が '0.0.0.0' になっていることを確認
```

**正しい設定**:
```typescript
// frontend/vite.config.ts
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // ← これが重要
    port: 3000,
    open: false
  }
})
```

**修正後の対応**:
```bash
# フロントエンドコンテナを再ビルド
docker-compose stop frontend
docker-compose up frontend --build -d
```

#### 2. バックエンドのパッケージインストールエラー

**症状**: `python-cors==1.0.1` のインストールでエラーが発生

**原因**: 存在しないパッケージが指定されている

**解決方法**:
```bash
# backend/requirements.txt を修正
# python-cors==1.0.1 → # CORS (FastAPI includes CORS middleware)
```

#### 3. ポートが既に使用されている

**症状**: `Port already in use` エラー

**解決方法**:
```bash
# 使用中のプロセスを確認
lsof -i :3000
lsof -i :8000
lsof -i :5050

# 既存のコンテナを停止
docker-compose down

# 必要に応じて強制停止
docker stop $(docker ps -aq)
```

## 📝 便利なコマンド

### 基本操作
```bash
# サービス起動
docker-compose up -d

# サービス停止
docker-compose down

# 特定サービスのみ起動
docker-compose up frontend backend -d

# ログ確認
docker-compose logs -f frontend
docker-compose logs -f backend

# コンテナ状態確認
docker-compose ps
```

### 開発時の操作
```bash
# サービス再ビルド
docker-compose up --build -d

# 特定サービスの再ビルド
docker-compose up frontend --build -d

# コンテナ内でコマンド実行
docker-compose exec frontend sh
docker-compose exec backend bash

# データベース接続
docker-compose exec db psql -U postgres -d whiteboard_dev

# pgAdmin管理
docker-compose exec pgadmin /bin/sh
```

### pgAdmin設定
```bash
# pgAdmin初期設定
# URL: http://localhost:5050/
# Email: admin@example.com
# Password: admin

# PostgreSQL サーバー追加:
# Host: db
# Port: 5432
# Database: whiteboard_dev
# Username: postgres
# Password: postgres
```

### クリーンアップ
```bash
# 停止 + コンテナ削除
docker-compose down

# 停止 + コンテナ削除 + ボリューム削除
docker-compose down -v

# 未使用のイメージ・コンテナ削除
docker system prune

# ビルドキャッシュもクリア
docker system prune -a
```

## 🌐 サービス構成

| サービス | URL | 説明 |
|---------|-----|------|
| Frontend | http://localhost:3000/ | Vue.js + Vite開発サーバー |
| Backend | http://localhost:8000/ | FastAPI サーバー |
| API Docs | http://localhost:8000/docs | Swagger UI |
| pgAdmin | http://localhost:5050/ | データベース管理ツール |
| PostgreSQL | localhost:5432 | 開発用データベース |
| Test PostgreSQL | localhost:5433 | テスト用データベース |

## 🔍 ヘルスチェック

### 動作確認方法
```bash
# フロントエンド確認
curl -I http://localhost:3000/

# バックエンド確認
curl http://localhost:8000/
# 期待値: {"message":"Whiteboard API is running"}

# ヘルスチェック
curl http://localhost:8000/health
# 期待値: {"status":"healthy"}
```

## 📋 開発フロー

### 初回セットアップ
1. リポジトリクローン
2. `.env` ファイル作成
3. `docker-compose up --build -d`
4. ブラウザで動作確認

### 日次開発
1. `docker-compose up -d` でサービス起動
2. 開発作業
3. `docker-compose down` で終了

### コード変更時
- **フロントエンド**: ホットリロード対応（自動反映）
- **バックエンド**: ホットリロード対応（自動反映）
- **Docker設定変更**: `docker-compose up --build -d` で再ビルド

## ⚠️ 注意事項

1. **初回起動は時間がかかります**
   - Node.jsとPythonのイメージダウンロード
   - 依存関係のインストール
   - 通常5-10分程度

2. **M1/M2 Mac での注意**
   - ARM64アーキテクチャ用のイメージが使用されます
   - 初回ビルド時間が長くなる場合があります

3. **ポート競合**
   - 3000, 8000, 5050, 5432, 5433番ポートが必要
   - 他のサービスと競合する場合は docker-compose.yml で変更可能

4. **データ永続化**
   - PostgreSQLデータは Docker Volume に保存
   - `docker-compose down -v` でデータも削除されます

## 📞 サポート

問題が発生した場合:
1. このドキュメントのトラブルシューティングを確認
2. `docker-compose logs [service]` でログを確認
3. GitHub Issues で報告

---

**最終更新**: 2025-06-29  
**対象バージョン**: Docker Desktop 4.x, Docker Compose 2.x