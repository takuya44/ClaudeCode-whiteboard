-- データベース初期化スクリプト
-- このファイルは実装計画書に従ってバックエンド担当者Aが詳細を実装してください

-- 開発用データベース作成（既に存在する場合はスキップ）
SELECT 'CREATE DATABASE whiteboard_dev'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'whiteboard_dev')\gexec

-- テスト用データベース作成（既に存在する場合はスキップ）  
SELECT 'CREATE DATABASE whiteboard_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'whiteboard_test')\gexec

-- TODO: バックエンド担当者Aが以下を実装
-- 1. ユーザーテーブル設計
-- 2. ホワイトボードテーブル設計
-- 3. 描画データテーブル設計
-- 4. 権限管理テーブル設計
-- 5. 初期データ投入

-- 実装例（詳細は担当者が設計）:
-- CREATE TABLE users (...);
-- CREATE TABLE whiteboards (...);
-- CREATE TABLE drawing_data (...);
-- CREATE TABLE permissions (...);