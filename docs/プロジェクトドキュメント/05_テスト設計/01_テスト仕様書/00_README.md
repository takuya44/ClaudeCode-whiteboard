# テスト仕様書

## 概要
このフォルダには、ホワイトボードプラットフォームの各テストレベルにおける詳細なテスト仕様書が含まれています。

## テスト仕様書一覧

### 基本テスト仕様書
- [01_単体テスト仕様書.md](./01_単体テスト仕様書.md) - コンポーネント・関数レベルのテスト
- [02_結合テスト仕様書.md](./02_結合テスト仕様書.md) - モジュール間連携テスト
- [03_システムテスト仕様書.md](./03_システムテスト仕様書.md) - エンドツーエンドシステムテスト
- [04_受入テスト仕様書.md](./04_受入テスト仕様書.md) - ユーザー受入テスト

### 非機能テスト仕様書
- [05_性能テスト仕様書.md](./05_性能テスト仕様書.md) - パフォーマンス・負荷テスト
- [06_セキュリティテスト仕様書.md](./06_セキュリティテスト仕様書.md) - セキュリティ脆弱性テスト

## テスト仕様書の構成

### 基本フォーマット
```markdown
## テストケース: [ID]_[機能名]_[テストタイプ]

### 目的
[テストの目的・確認内容]

### 前提条件
[テスト実行前の状態・設定]

### 入力データ
[テストで使用する入力値・パラメータ]

### 実行手順
1. [詳細な実行ステップ]
2. [期待される中間結果の確認]
3. [最終実行ステップ]

### 期待結果
[期待される出力・状態変化]

### 判定基準
[合格・不合格の判定方法]
```

## テストID命名規則

### 形式
`[Level][Module][Function][Type][Number]`

### 例
- `UT_AUTH_LOGIN_NORMAL_001`: 単体テスト_認証_ログイン_正常系_001
- `IT_API_WHITEBOARD_ERROR_005`: 統合テスト_API_ホワイトボード_異常系_005
- `ST_E2E_COLLABORATION_NORMAL_010`: システムテスト_E2E_コラボレーション_正常系_010

### 略語説明
- **Level**: UT(単体), IT(統合), ST(システム), AT(受入), PT(性能), SET(セキュリティ)
- **Module**: AUTH(認証), API(API), WB(ホワイトボード), COLLAB(コラボレーション)
- **Type**: NORMAL(正常系), ERROR(異常系), BOUNDARY(境界値)

## テストカバレッジ

### 機能カバレッジ
- **認証機能**: 100% (ログイン・登録・パスワード変更)
- **ホワイトボード操作**: 100% (作成・編集・削除・共有)
- **描画機能**: 100% (pen・line・rectangle・circle・text・sticky)
- **リアルタイム機能**: 100% (WebSocket通信・同期)
- **ユーザー管理**: 100% (プロフィール・権限管理)

### コードカバレッジ目標
- **単体テスト**: 80%以上
- **統合テスト**: 70%以上
- **E2Eテスト**: 60%以上

## テストデータ管理

### テストユーザー
```json
{
  "admin_user": {
    "email": "admin@test.example.com",
    "password": "AdminPass123!",
    "role": "admin"
  },
  "normal_user": {
    "email": "user@test.example.com", 
    "password": "UserPass123!",
    "role": "user"
  },
  "guest_user": {
    "email": "guest@test.example.com",
    "password": "GuestPass123!",
    "role": "guest"
  }
}
```

### テストホワイトボード
```json
{
  "public_whiteboard": {
    "title": "公開テストホワイトボード",
    "is_public": true,
    "elements_count": 10
  },
  "private_whiteboard": {
    "title": "プライベートテストホワイトボード",
    "is_public": false,
    "elements_count": 5
  },
  "large_whiteboard": {
    "title": "大容量テストホワイトボード",
    "elements_count": 1000
  }
}
```

## 実行環境

### テスト環境構成
- **OS**: Ubuntu 20.04 LTS
- **ブラウザ**: Chrome 114+, Firefox 115+, Safari 16+, Edge 114+
- **Node.js**: 18.x
- **Python**: 3.11.x
- **PostgreSQL**: 15.x

### テストツール
- **フロントエンド**: Vitest 0.32+, Playwright 1.35+
- **バックエンド**: pytest 7.4+, httpx 0.24+
- **性能テスト**: K6 0.45+, Artillery 2.0+
- **セキュリティ**: OWASP ZAP 2.12+, Snyk CLI

---
**最終更新**: 2024年7月6日