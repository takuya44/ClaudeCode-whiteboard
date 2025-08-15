# コードスタイルと規約

## フロントエンド (Vue 3 + TypeScript)

### ESLint設定
- Vue 3 essential、strongly-recommended、recommended ルール適用
- TypeScript ESLint パーサー使用
- Vue 3専用ルール設定
- コンソール・デバッガー: 開発環境では許可、プロダクションでは警告
- `vue/multi-word-component-names`: 無効
- `vue/no-v-html`: 無効

### Prettier設定
- **セミコロン**: なし (`"semi": false`)
- **クォート**: シングル (`"singleQuote": true`)
- **タブ幅**: 2スペース (`"tabWidth": 2`)
- **末尾カンマ**: ES5互換 (`"trailingComma": "es5"`)
- **行幅**: 80文字 (`"printWidth": 80`)
- **改行コード**: LF (`"endOfLine": "lf"`)
- **アロー関数**: 括弧を避ける (`"arrowParens": "avoid"`)
- **Vue インデント**: スクリプト・スタイルブロックはインデントしない

### TypeScript設定
- ES2022以降の機能使用
- 厳格な型チェック有効
- Vue.js向けの型設定

## バックエンド (FastAPI + Python)

### Pylint設定 (.pylintrc)
- **最大行長**: 120文字
- **無効化された警告**:
  - SQLAlchemy関連: `too-few-public-methods`, `no-member`
  - Pydantic関連: `unused-argument`
  - ドキュメント関連: `missing-*-docstring`
  - 複雑度関連: `too-many-*`

### Python コード品質ツール
- **Black**: コードフォーマッター (23.11.0)
- **Flake8**: リンター (6.1.0)
- **isort**: インポート文整理 (5.12.0)

### 命名規約
- **関数・変数**: snake_case
- **クラス**: PascalCase
- **定数**: UPPER_CASE
- **プライベート**: 先頭にアンダースコア

## コミット規約
```
feat: 新機能
fix: バグ修正
docs: ドキュメント
style: コードスタイル
refactor: リファクタリング
test: テスト
chore: 雑務
```

## コードレビューガイドライン
- 型安全性の確保
- セキュリティ考慮
- パフォーマンス最適化
- 可読性・保守性の向上