/**
 * Vitest テストセットアップファイル
 * 
 * このファイルは全てのテストファイルが実行される前に自動的に読み込まれ、
 * テスト実行に必要な共通設定や環境構築を行います。
 * 
 * 主な役割：
 * - ブラウザ環境のモック（localStorage、window.locationなど）
 * - 外部ライブラリのモック設定
 * - Vue.js テスト環境の初期化
 * - 各テスト実行前後の共通処理
 */

import { vi, beforeEach, afterEach } from 'vitest'
import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'

// 【Vue Test Utils グローバル設定】
// 国際化（i18n）機能のモック：翻訳キーをそのまま返すシンプルな関数
if (config.global.config.globalProperties) {
  config.global.config.globalProperties.$t = (key: string) => key
}

// 【ブラウザAPI モック１】ローカルストレージ（データ保存機能）の偽物
// 実際のブラウザのlocalStorageを使わずに、テスト用の偽物を作成
const localStorageMock = {
  getItem: vi.fn(),    // データ取得：常にundefinedを返す偽物
  setItem: vi.fn(),    // データ保存：何もしない偽物
  removeItem: vi.fn(), // データ削除：何もしない偽物
  clear: vi.fn(),      // 全削除：何もしない偽物
}
// windowオブジェクトのlocalStorageを上記の偽物に置き換え
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// 【ブラウザAPI モック２】window.location（URL情報）の偽物
// 実際のブラウザのURL情報を使わずに、テスト用の固定値を設定
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',      // 完全なURL
    origin: 'http://localhost:3000',    // プロトコル+ドメイン
    pathname: '/',                      // パス部分
    search: '',                         // クエリパラメータ部分
    hash: '',                          // ハッシュ部分
  },
  writable: true  // テスト中に値を変更可能にする
})

// 【各テスト実行前の共通処理】
// 全てのテストファイルの各テストケース実行前に必ず実行される処理
beforeEach(() => {
  // Vue.js状態管理（Pinia）の新しいインスタンスを作成
  // これにより、各テストが独立した状態で実行される（テスト間の影響を防ぐ）
  const pinia = createPinia()
  config.global.plugins = [pinia]
})

// 【環境変数モック】開発用環境変数の偽物
// import.meta.env（Vite特有の環境変数）にテスト用の値を設定
vi.mock('import.meta', () => ({
  env: {
    VITE_API_URL: 'http://localhost:8000'  // バックエンドAPIのURLを固定値に
  }
}))

// 【外部ライブラリモック】@vueform/multiselect の偽物
// 複雑なマルチセレクトコンポーネントをシンプルなdivに置き換え
// これにより、外部ライブラリに依存しない純粋なコンポーネントテストが可能
vi.mock('@vueform/multiselect', () => ({
  default: {
    name: 'Multiselect',                                           // コンポーネント名
    template: '<div class="mock-multiselect"><slot /></div>',      // シンプルなHTML
    props: ['modelValue', 'options', 'multiple', 'searchable'],    // 必要な属性のみ
    emits: ['update:modelValue', 'change']                         // 発行されるイベント
  }
}))

// 【各テスト実行後のクリーンアップ処理】
// 全てのテストファイルの各テストケース実行後に必ず実行される処理
afterEach(() => {
  // 全てのモック関数の呼び出し履歴をクリア（次のテストに影響しないように）
  vi.clearAllMocks()
  
  // ローカルストレージモックの呼び出し履歴も個別にクリア
  localStorageMock.getItem.mockClear()
  localStorageMock.setItem.mockClear()
  localStorageMock.removeItem.mockClear()
  localStorageMock.clear.mockClear()
})