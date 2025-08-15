# プロジェクト概要

## プロジェクトの目的
オンラインホワイトボードアプリケーション - リアルタイムの協業型デジタルホワイトボード

## 主な機能
- リアルタイムでの共同編集
- WebSocketを使用したリアルタイム通信
- 図形描画機能
- 高度な検索機能（タグ、作成者、日付範囲での絞り込み）

## アーキテクチャ
- **フロントエンド**: Vue 3 + TypeScript (SPA)
- **バックエンド**: FastAPI + Python 3.10
- **データベース**: PostgreSQL 15
- **通信**: WebSocket for リアルタイム通信
- **開発環境**: Docker + Docker Compose

## 開発環境
- Docker Composeによる完全なマルチコンテナセットアップ
- ホットリロード対応（開発環境）
- pgAdminによるデータベース管理GUI

## デプロイ構成
- フロントエンド: http://localhost:3000
- バックエンド API: http://localhost:8000  
- API ドキュメント: http://localhost:8000/docs
- pgAdmin: http://localhost:5050