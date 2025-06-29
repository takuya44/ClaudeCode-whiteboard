# デプロイ戦略

## 1. デプロイ環境

### 1.1 環境構成
- **開発環境**: Docker Compose（ローカル）
- **ステージング環境**: Docker + オーケストレーション
- **本番環境**: クラウドプロバイダー

### 1.2 推奨クラウドプロバイダー
1. **AWS**: ECS + RDS + ALB
2. **GCP**: Cloud Run + Cloud SQL + Load Balancer  
3. **Azure**: Container Instances + Database + Application Gateway

## 2. コンテナ化戦略

### 2.1 本番用Dockerfile

**Backend (FastAPI)**
```dockerfile
# backend/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home app && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend (Vue 3)**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2.2 本番用Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=${API_URL}
      - VITE_WS_URL=${WS_URL}

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 3. CI/CDパイプライン

### 3.1 GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          # クラウドプロバイダー固有のデプロイコマンド
```

### 3.2 環境変数管理
```bash
# 本番環境変数例
DATABASE_URL=postgresql://user:pass@prod-db:5432/whiteboard
SECRET_KEY=production-secret-key
API_URL=https://api.whiteboard.com
WS_URL=wss://api.whiteboard.com/ws
ENVIRONMENT=production
DEBUG=False
```

## 4. クラウド別デプロイガイド

### 4.1 AWS デプロイ
```bash
# ECS + RDS構成
aws ecs create-cluster --cluster-name whiteboard-cluster
aws rds create-db-instance --db-name whiteboard \
  --db-instance-identifier whiteboard-db \
  --db-instance-class db.t3.micro
```

### 4.2 GCP デプロイ
```bash
# Cloud Run + Cloud SQL構成  
gcloud run deploy whiteboard-backend \
  --source ./backend \
  --platform managed \
  --region asia-northeast1

gcloud sql instances create whiteboard-db \
  --database-version POSTGRES_14 \
  --region asia-northeast1
```

### 4.3 Azure デプロイ
```bash
# Container Instances + Database構成
az container create \
  --resource-group whiteboard-rg \
  --name whiteboard-backend \
  --image whiteboard/backend

az postgres server create \
  --resource-group whiteboard-rg \
  --name whiteboard-db
```

## 5. インフラ構成

### 5.1 ネットワーク構成
```
[Load Balancer] → [Frontend Containers] → [Backend Containers] → [Database]
                                      ↓
                                 [WebSocket Connections]
```

### 5.2 スケーリング戦略
- **フロントエンド**: CDN + 複数レプリカ
- **バックエンド**: 水平スケーリング（2-10インスタンス）
- **データベース**: リードレプリカ + 接続プーリング
- **WebSocket**: ロードバランサーでセッション維持

### 5.3 監視・ロギング
```bash
# 監視ツール
- アプリケーション監視: New Relic / DataDog
- インフラ監視: CloudWatch / Stackdriver
- ログ集約: ELK Stack / Cloud Logging
- エラー追跡: Sentry
```

## 6. セキュリティ

### 6.1 HTTPS/SSL
```nginx
# nginx設定例
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://backend:8000;
    }
    
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 6.2 環境分離
```bash
# 環境別設定
development:
  - ローカルDocker
  - 開発用DB
  - デバッグ有効

staging:
  - クラウド環境
  - 本番データのコピー
  - パフォーマンステスト

production:
  - 冗長化構成
  - バックアップ
  - 監視・アラート
```

## 7. バックアップ・災害復旧

### 7.1 データベースバックアップ
```bash
# 自動バックアップ設定
# AWS RDS: 自動バックアップ有効
# GCP Cloud SQL: 自動バックアップ有効
# Azure Database: 自動バックアップ有効

# 手動バックアップ
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > backup.sql
```

### 7.2 アプリケーションバックアップ
```bash
# コンテナイメージのバックアップ
docker save whiteboard/backend:latest > backend-backup.tar
docker save whiteboard/frontend:latest > frontend-backup.tar
```

## 8. パフォーマンス最適化

### 8.1 フロントエンド最適化
- バンドルサイズ最適化
- 画像圧縮
- CDN利用
- キャッシュ戦略

### 8.2 バックエンド最適化
- データベース接続プーリング
- Redis キャッシュ（必要に応じて）
- WebSocket接続管理
- APIレスポンス最適化

## 9. デプロイメントチェックリスト

### 9.1 デプロイ前確認
- [ ] テスト実行
- [ ] セキュリティスキャン
- [ ] パフォーマンステスト
- [ ] 環境変数設定
- [ ] データベースマイグレーション

### 9.2 デプロイ後確認  
- [ ] ヘルスチェック
- [ ] 機能テスト
- [ ] WebSocket接続テスト
- [ ] 監視設定
- [ ] ログ確認