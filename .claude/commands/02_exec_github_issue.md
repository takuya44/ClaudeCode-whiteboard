# /02_exec_github_issue

## 使い方

```
/02_exec_github_issue <issue番号> [オプション]
```

指定された GitHub issue の内容を実装します。

### 基本使用例

```
/02_exec_github_issue 123                    # 通常の実装フロー
/02_exec_github_issue 45 --kiro-spec        # Kiro仕様書ベースの実装
/02_exec_github_issue 67 --no-branch        # 現在のブランチで実装
/02_exec_github_issue 89 --draft            # ドラフト実装（テスト・lintスキップ）
/02_exec_github_issue 101 --no-commit       # 実装のみでコミットなし
/02_exec_github_issue 202 --quick           # 簡易実装モード
/02_exec_github_issue 303 --single-task --task-id "8.1" # 単一タスク実装（8.1ユニットテスト実装）
```

### オプション一覧

| オプション | 説明 | 動作 |
|-----------|------|------|
| `--no-branch` | ブランチ作成をスキップ | 現在のブランチで直接作業 |
| `--no-commit` | コミット作成をスキップ | 実装完了後にコミットを作成しない |
| `--draft` | ドラフト実装モード | テスト実行とlint/typecheckをスキップ |
| `--kiro-spec` | Kiro仕様書ベース実装 | `.kiro/specs/`の該当仕様書を参照して実装 |
| `--quick` | 簡易実装モード | セルフレビューを簡略化、基本的な確認のみ |
| `--single-task` | 単一タスク実装モード | 指定されたチェックリスト項目のみを実装 |
| `--task-id <識別子>` | タスク識別子指定 | 実装対象のチェックリスト項目を指定 |

### 複合オプション使用例

```
/02_exec_github_issue 123 --draft --no-commit          # ドラフト実装、コミットなし
/02_exec_github_issue 456 --kiro-spec --quick          # Kiro仕様書ベース、簡易モード
/02_exec_github_issue 789 --no-branch --no-commit      # 現在ブランチ、コミットなし
/02_exec_github_issue 101 --single-task --task-id "8.2" --draft  # 単一タスク、ドラフトモード
/02_exec_github_issue 202 --single-task --task-id "9.1" --kiro-spec  # 単一タスク、仕様書ベース
```

### 単一タスク実装モードの詳細

`--single-task` オプションを使用する場合の特別な指定方法：

#### タスク識別子の指定方法

1. **セクション番号**: `--task-id "8.1"` （例：8.1 ユニットテスト実装）
2. **チェックリスト項目**: `--task-id "フロントエンド"` （例：フロントエンドユニットテスト）
3. **行範囲**: `--task-id "L15-L25"` （例：issue の15-25行目のタスク）
4. **キーワード**: `--task-id "Vitest"` （例：Vitest関連のタスクのみ）

#### 使用例（膨大なタスクの場合）

```
# 8.1 ユニットテスト実装のフロントエンド部分のみ
/02_exec_github_issue 303 --single-task --task-id "8.1" --task-id "フロントエンド"

# パフォーマンステストのバックエンド最適化のみ  
/02_exec_github_issue 303 --single-task --task-id "9.1" --draft

# E2Eテストの主要シナリオテストのみ
/02_exec_github_issue 303 --single-task --task-id "8.3" --task-id "主要シナリオ"
```

## 実行内容

`gh issue view <issue番号>` で issue を確認し、指定されたオプションに応じて以下の手順で実装を進めます：

### 1. 準備フェーズ

#### 基本準備（全オプション共通）
- [ ] Issue の内容を理解
- [ ] `--kiro-spec` オプション時：`.kiro/specs/`の該当仕様書（requirements.md、design.md、tasks.md）を確認
- [ ] `--single-task` オプション時：指定されたタスク識別子に基づいて対象チェックリスト項目を特定

#### ブランチ管理（`--no-branch` オプション時はスキップ）
- [ ] main ブランチに切り替えて最新状態を取得 (`git checkout main && git pull`)
- [ ] 適切な名前でブランチを作成 (例: `feature/issue-123-add-user-auth`)

### 2. 実装フェーズ

#### 通常モード
- [ ] 必要なタスクを Todo リストで管理
- [ ] Issue の要件に従って実装
- [ ] `--kiro-spec` オプション時：仕様書のタスクリストに従って実装

#### `--single-task` モード
- [ ] 指定されたチェックリスト項目のみに集中して実装
- [ ] 関連する他のタスクは対象外として明示的に除外
- [ ] 該当するテストファイル・設定ファイルのみを変更
- [ ] 実装完了後に指定されたチェックリスト項目にチェックマークを追加

### 3. 品質確認フェーズ

#### 通常モード
- [ ] セルフレビュー実施（`../../docs/プロジェクトドキュメント/04_開発ガイドライン/04_レビューガイドライン.md`参照）
- [ ] テスト実行（該当する場合）
- [ ] lint/typecheck 実行

#### `--quick` オプション時
- [ ] 基本的な動作確認のみ
- [ ] 重要な lint エラーのみチェック

#### `--draft` オプション時
- [ ] コード動作確認のみ（テスト・lint/typecheckはスキップ）

### 4. コミット作成フェーズ（`--no-commit` オプション時はスキップ）

- [ ] 変更内容を確認（`git status`, `git diff`）
- [ ] **ユーザーに実装内容を説明し、承認を得る**
- [ ] 承認後、適切な粒度でコミット作成
- [ ] コミットメッセージは issue 番号を含める（例: `feat: ユーザー認証機能を追加 #123`）

## 注意事項

### 基本ルール
- **重要**: このコマンドでは `git push` は禁止です。push はユーザーが手動で行ってください
- Issue の要件が不明確な場合は、実装前に確認
- 大きなタスクは適切に分割して実装
- コミット前に必ずユーザーの承認を得る（`--no-commit` オプション時を除く）

### オプション使用時の注意

#### `--no-branch` オプション
- 現在のブランチで直接作業するため、作業前に適切なブランチにいることを確認
- main ブランチでの直接作業は避ける

#### `--draft` オプション
- テストやlintをスキップするため、本格実装前の試行錯誤用途に限定
- 最終実装時は通常モードで品質確認を実施

#### `--kiro-spec` オプション
- 該当する仕様書が `.kiro/specs/` に存在することを事前確認
- 仕様書の内容が最新でない場合は、issue の内容を優先

#### `--quick` オプション
- 品質確認を簡略化するため、重要な機能には使用を避ける
- 小さな修正やホットフィックス用途に限定

#### `--single-task` オプション
- 膨大なタスクリストを持つissueで実装品質を担保するために使用
- `--task-id` で指定されたタスクのみに集中し、他のタスクには触れない
- 複数の `--task-id` を指定して、関連するタスクのみを同時実装可能
- 大規模issue（20+チェックリスト項目）での使用を推奨

#### `--task-id` オプション
- `--single-task` オプションと組み合わせて使用必須
- セクション番号（"8.1"）、キーワード（"フロントエンド"）、行範囲（"L15-L25"）で指定可能
- 複数指定により、関連タスクをまとめて実装可能

### オプション組み合わせ時
- 複数オプションの組み合わせ時は、各オプションの制約を理解して使用
- 特に `--draft` と `--no-commit` の組み合わせは試行錯誤用途に適している
- `--single-task` + `--draft` の組み合わせは、大規模issueでの試行錯誤に最適
- `--single-task` + `--kiro-spec` で仕様書ベースの部分実装が可能

### 推奨使用パターン

#### 膨大なissue（20+項目）の場合
```bash
# フェーズ別で段階的実装
/02_exec_github_issue 303 --single-task --task-id "8.1" --draft
/02_exec_github_issue 303 --single-task --task-id "8.2" --kiro-spec  
/02_exec_github_issue 303 --single-task --task-id "8.3"

# 関連タスクをまとめて実装
/02_exec_github_issue 303 --single-task --task-id "フロントエンド" --task-id "Vitest"
```

#### 通常のissue（10項目以下）の場合
```bash
/02_exec_github_issue 123 --kiro-spec    # 仕様書ベース実装
/02_exec_github_issue 456 --quick        # 簡易実装
```
