# プロジェクトドキュメント

オンラインホワイトボードアプリのドキュメント管理

## 📁 ドキュメント構成

```
docs/
├── README.md                    # このファイル（ドキュメント索引）
├── progress-summary.md          # 🔥 プロジェクト進捗サマリー（全体状況把握）
├── requirements/                # 要件定義
│   ├── requirements.md         # メイン要件定義書
│   ├── functional.md           # 機能要件詳細
│   ├── non-functional.md       # 非機能要件詳細
│   └── user-stories.md         # ユーザーストーリー
├── design/                      # 設計書
│   ├── system-architecture.md  # システム構成
│   ├── database-design.md      # データベース設計
│   ├── api-design.md           # API設計
│   ├── frontend-design.md      # フロントエンド設計
│   └── realtime-design.md      # リアルタイム通信設計
├── deployment/                  # デプロイ関連
│   ├── deployment.md           # デプロイ戦略
│   ├── infrastructure.md       # インフラ構成
│   ├── ci-cd.md               # CI/CDパイプライン
│   └── monitoring.md          # 監視・運用
├── development/                 # 開発関連
│   ├── setup.md               # 開発環境セットアップ
│   ├── coding-standards.md    # コーディング規約
│   ├── implementation-plan.md # 実装計画書
│   ├── git-workflow.md        # Git運用ルール
│   └── testing.md             # テスト戦略
└── logs/                        # 作業記録
    ├── README.md              # 作業記録管理ガイド
    ├── template_daily.md      # 日次記録テンプレート
    ├── template_weekly.md     # 週次記録テンプレート
    └── YYYY-MM-DD_task.md     # 実際の作業記録
```

## 📋 ドキュメント一覧

### 🔥 プロジェクト進捗
| ファイル | 説明 | 最終更新 |
|---------|------|----------|
| [progress-summary.md](./progress-summary.md) | **プロジェクト全体の進捗状況と成果物サマリー** | 2025-07-01 |

### 要件定義 (requirements/)
| ファイル | 説明 | 最終更新 |
|---------|------|----------|
| [requirements.md](./requirements/requirements.md) | プロジェクト全体要件定義 | 2025-06-29 |

### 設計書 (design/)
| ファイル | 説明 | 最終更新 |
|---------|------|----------|
| - | 設計書は今後作成予定 | - |

### デプロイ (deployment/)
| ファイル | 説明 | 最終更新 |
|---------|------|----------|
| [deployment.md](./deployment/deployment.md) | デプロイ戦略・手順 | 2025-06-29 |

### 開発 (development/)
| ファイル | 説明 | 最終更新 |
|---------|------|----------|
| [setup.md](./development/setup.md) | 開発環境セットアップガイド | 2025-06-29 |
| [docker-setup.md](./development/docker-setup.md) | **Docker起動手順書（トラブルシューティング付き）** | 2025-06-29 |
| [coding-standards.md](./development/coding-standards.md) | コーディング規約 | 2025-06-29 |
| [implementation-plan.md](./development/implementation-plan.md) | 4人チーム実装計画書 | 2025-06-29 |

### 作業記録 (logs/)
| ファイル | 説明 | 最終更新 |
|---------|------|----------|
| [README.md](./logs/README.md) | 作業記録管理ガイド | 2025-06-29 |
| [2025-06-29_project-setup.md](./logs/2025-06-29_project-setup.md) | プロジェクト初期構成作業記録 | 2025-06-29 |

## 🔄 ドキュメント更新ルール

### 1. 新規ドキュメント作成時
1. 適切なディレクトリに配置
2. この README.md の一覧表を更新
3. 最終更新日を記録

### 2. 既存ドキュメント更新時
1. 最終更新日を変更
2. 変更内容を簡潔に記録（必要に応じて）

### 3. ドキュメント命名規則
- ファイル名: kebab-case（例: `api-design.md`）
- 日本語可能だが英語推奨
- 内容が分かりやすい名前

## 📝 テンプレート

新しいドキュメント作成時は以下のテンプレートを参考に：

### 技術設計書テンプレート
```markdown
# [タイトル]

## 概要
[簡潔な説明]

## 背景・目的
[なぜこの設計が必要か]

## 設計詳細
[具体的な設計内容]

## 技術選定理由
[選択した技術の理由]

## 実装方針
[実装時の注意点]

## 参考資料
[関連ドキュメント・外部リンク]
```

## 🔍 検索・参照方法

### よく参照されるドキュメント
1. **プロジェクト状況確認**: [progress-summary.md](./progress-summary.md) 🔥**最重要**
2. **開発開始時**: [requirements.md](./requirements/requirements.md)
3. **環境構築時**: [../README.md](../README.md) または [docker-setup.md](./development/docker-setup.md)
4. **Docker起動問題**: [docker-setup.md](./development/docker-setup.md)
5. **デプロイ時**: [deployment.md](./deployment/deployment.md)

### ドキュメント検索
```bash
# プロジェクトルートから
grep -r "検索キーワード" docs/
find docs/ -name "*.md" -exec grep -l "検索キーワード" {} \;
```

## 📊 ドキュメント状況

- ✅ 完了: 要件定義、デプロイ戦略、実装計画書、開発環境構築
- 🚧 進行中: -
- 📋 予定: システム設計、API設計、データベース設計

## 🎯 現在の状況（2025-06-29）

### Phase 1: プロジェクト基盤構築 ✅完了
- 要件定義・設計完了
- Docker環境構築完了  
- 4人チーム実装計画書完了
- プロジェクト初期構成完了

### Phase 2: 基盤実装 ⏳次のステップ
明日からWeek 3タスク開始予定
詳細は [implementation-plan.md](./development/implementation-plan.md) を参照

## 📞 質問・提案

ドキュメントに関する質問や改善提案があれば：
1. GitHub Issue作成
2. 開発チームMTGで相談
3. 直接担当者に連絡