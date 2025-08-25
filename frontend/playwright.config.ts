import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2Eテストの設定ファイル
 * 
 * この設定ファイルの目的：
 * - 複数ブラウザでのテスト実行環境を定義
 * - CI/CD環境と開発環境での動作を最適化
 * - テスト結果のレポート生成とアーティファクト（証拠資料）保存を設定
 * - 開発サーバーの自動起動による効率的なテスト実行
 * 
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // E2Eテストファイルが格納されているディレクトリを指定
  testDir: './e2e',
  
  // 並列実行の設定：複数のテストを同時実行してテスト時間を短縮
  fullyParallel: true,
  
  // CI環境でtest.onlyが残っていた場合のビルド失敗設定
  // 開発者が特定のテストのみ実行する設定を本番に残すミスを防ぐ
  forbidOnly: !!process.env.CI,
  
  // リトライ（再試行）設定
  // CI環境：ネットワークの不安定さなどを考慮して2回まで再試行
  // ローカル開発：即座に失敗原因を把握するため再試行しない
  retries: process.env.CI ? 2 : 0,
  
  // ワーカー数（並列実行数）の設定
  // CI環境：リソース制限を考慮して1つずつ実行
  // ローカル開発：CPUコア数に応じて自動最適化
  workers: process.env.CI ? 1 : undefined,
  // テストレポーターの設定（テスト結果の出力形式）
  // 複数の形式でレポートを生成し、異なる用途に対応
  reporter: [
    ['html'],  // HTMLレポート：ブラウザで見やすいレポート（開発者向け）
    ['junit', { outputFile: 'test-results/junit.xml' }], // JUnitXML：CI/CDツールとの連携用
  ],
  
  // 全プロジェクト共通の設定
  // ここで設定した内容は、後述の全ブラウザ設定に適用される
  use: {
    // ベースURL：テスト中の`await page.goto('/')`などで使用される基準URL
    // Vite開発サーバーのデフォルトポート
    baseURL: 'http://localhost:5173',
    
    // トレース機能：テスト失敗時の詳細な実行履歴を記録
    // 'on-first-retry'：初回失敗後の再試行時にのみ記録（ファイルサイズを抑制）
    trace: 'on-first-retry',
    
    // スクリーンショット撮影：テスト失敗時のみ画面キャプチャを保存
    // デバッグ時に失敗した画面状態を確認できる
    screenshot: 'only-on-failure',
    
    // 動画録画：テスト失敗時のみ操作の様子を録画保存
    // 失敗に至るまでの操作手順を動画で確認可能
    video: 'retain-on-failure',
  },

  // テストプロジェクト設定：複数のブラウザ・デバイスでテストを実行
  // 実際のユーザーが使用する様々な環境での動作を保証
  projects: [
    {
      // Chromiumブラウザ（Chrome系）でのテスト
      // 最も広く使用されているブラウザエンジン
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      // Firefoxブラウザでのテスト  
      // Geckoエンジン使用、ChromiumとWebKitとは異なる動作をする場合がある
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      // WebKitブラウザ（Safari系）でのテスト
      // macOS/iOS環境での動作確認に重要
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // モバイルデバイスでのテスト
    // レスポンシブデザインとタッチ操作の動作確認
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] }, // Android端末を模擬
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] }, // iOS端末を模擬
    },

    // 追加のブラウザテスト（必要に応じてコメントアウトを解除）
    // 特定のブラウザでの問題が発見された場合に有効化
    // {
    //   name: 'Microsoft Edge',
    //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    // },
  ],

  // 開発サーバーの自動起動設定
  // テスト実行前にアプリケーションサーバーを自動的に起動
  webServer: {
    // 起動コマンド：Vite開発サーバーを起動
    command: 'npm run dev',
    
    // サーバーのURL：テストがこのURLに対してリクエストを送信
    url: 'http://localhost:5173',
    
    // 既存サーバーの再利用設定
    // ローカル開発：既に起動中のサーバーがあれば再利用（開発効率向上）
    // CI環境：毎回新しいサーバーを起動（環境の一貫性保証）
    reuseExistingServer: !process.env.CI,
    
    // サーバー起動のタイムアウト時間（2分）
    // Viteの起動や依存関係のインストールに時間がかかる場合に対応
    timeout: 120 * 1000,
  },
})