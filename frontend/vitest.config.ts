/**
 * Vitest 設定ファイル
 * 
 * このファイルはVitestテストランナーの動作を制御する設定ファイルです。
 * テスト実行環境、カバレッジ計測、ファイルパス解決などの設定を定義します。
 * 
 * 主な設定内容：
 * - テスト実行環境（jsdom = ブラウザ環境のシミュレート）
 * - カバレッジ測定（テストでどれだけコードが実行されたかの計測）
 * - セットアップファイルの指定
 * - ファイルパス解決（@/ → src/ への変換）
 */

/// <reference types="vitest" />
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  // 【プラグイン設定】使用するViteプラグインの指定
  plugins: [vue()],  // Vue.js単一ファイルコンポーネント（.vue）を処理するプラグイン
  
  // 【テスト設定】Vitestテストランナーの詳細設定
  test: {
    // テスト実行環境：jsdom = ブラウザ環境をNode.js上でシミュレート
    // これにより、window、document、localStorageなどのブラウザAPIが使用可能
    environment: 'jsdom',
    
    // グローバルAPI：describe、it、expect などを全テストファイルでimport不要にする
    // 各テストファイルで「import { describe, it, expect } from 'vitest'」を省略可能
    globals: true,
    
    // セットアップファイル：全テスト実行前に自動的に読み込まれるファイル
    // モック設定や共通の初期化処理を記述
    setupFiles: ['src/__tests__/setup.ts'],
    
    // 【カバレッジ設定】テストでどれだけのコードが実行されたかを計測
    coverage: {
      // カバレッジ計測エンジン：V8エンジンの内蔵機能を使用（高速で正確）
      provider: 'v8',
      
      // レポート出力形式
      reporter: [
        'text',   // コンソールにテキスト形式で表示
        'html',   // ブラウザで見れるHTML形式のレポート生成
        'lcov'    // CI/CDツールで使用される標準形式
      ],
      
      // カバレッジ計測から除外するファイル・フォルダ
      exclude: [
        'node_modules/',        // サードパーティライブラリ
        'src/__tests__/',       // テストファイル自体
        'src/**/*.test.ts',     // 個別テストファイル
        'src/**/*.spec.ts',     // 個別スペックファイル
        '**/*.d.ts',           // TypeScript型定義ファイル
        'src/main.ts'          // アプリケーションエントリーポイント
      ],
      
      // 【カバレッジ閾値】テストの品質基準を設定（90%以上を要求）
      // この基準を下回るとテスト実行が失敗扱いになる
      thresholds: {
        global: {
          branches: 90,    // 分岐（if文、switch文など）のカバレッジ90%以上
          functions: 90,   // 関数のカバレッジ90%以上
          lines: 90,       // 行のカバレッジ90%以上
          statements: 90   // 文のカバレッジ90%以上
        }
      }
    }
  },
  
  // 【ファイルパス解決設定】インポート時のパス変換ルール
  resolve: {
    alias: {
      // '@/' を 'src/' に変換（例：'@/components/Button' → 'src/components/Button'）
      // これにより、深い階層からでも短いパスでファイルを参照可能
      '@': resolve(__dirname, 'src')
    }
  }
})