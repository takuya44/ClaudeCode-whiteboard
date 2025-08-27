/**
 * 検索ストア（Pinia）のテストファイル
 * 
 * このファイルでは、検索機能の状態管理を行うPiniaストアが
 * 正しく動作することをテストしています。
 * 
 * テストする機能：
 * - フィルター条件の管理（タグ、作成者、日付範囲）
 * - 検索結果の保存と表示
 * - ページネーション（ページ移動）の状態管理
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useSearchStore } from '../search'

// 【モック設定】APIモジュールの偽物を作成
// 実際のサーバー通信をせずに、テスト用の決まった値を返すようにする
vi.mock('@/api/search', () => ({
  searchAPI: {
    // 検索APIの偽物：常に空の結果を返す
    searchWhiteboards: vi.fn().mockResolvedValue({
      results: [],           // 検索結果なし
      total: 0,             // 総件数0
      page: 1,              // 1ページ目
      pageSize: 10,         // 1ページに10件表示
      hasNext: false        // 次のページなし
    }),
    // 利用可能なタグ一覧の偽物：空配列を返す
    getAvailableTags: vi.fn().mockResolvedValue([]),
    // 利用可能な作成者一覧の偽物：空配列を返す
    getAvailableAuthors: vi.fn().mockResolvedValue([])
  }
}))

// 【モック設定】デバウンス機能の偽物
// リアルタイム検索で使用される遅延処理を無効化（テストでは即座に実行）
vi.mock('@/utils/debounce', () => ({
  debounce: (fn: Function) => fn  // 関数をそのまま実行（遅延なし）
}))

describe('Search Store (Simplified)', () => {
  let store: ReturnType<typeof useSearchStore>

  // 【テスト前準備】各テストの実行前に必ず実行される処理
  beforeEach(() => {
    setActivePinia(createPinia())  // Piniaストア環境を初期化
    store = useSearchStore()       // 検索ストアのインスタンスを取得
  })

  // 【テスト1】ストアが正しい初期状態で開始されることを確認
  it('正しい初期状態を持つ', () => {
    // フィルター条件が空の状態で初期化されているかチェック
    expect(store.filters).toEqual({
      tags: [],              // 選択されたタグなし
      authors: [],           // 選択された作成者なし
      dateRange: {           // 日付範囲設定なし
        start: null,
        end: null,
        type: 'created'      // デフォルトは作成日基準
      },
      sortBy: 'updated_at',  // デフォルトは更新日順
      sortOrder: 'desc'      // デフォルトは降順（新しい順）
    })
    
    // 検索結果関連が空の状態で初期化されているかチェック
    expect(store.searchResults).toEqual([])  // 検索結果なし
    expect(store.totalResults).toBe(0)       // 総件数0
    expect(store.currentPage).toBe(1)        // 1ページ目
    expect(store.isLoading).toBe(false)      // ローディング中ではない
  })

  // 【テスト2】フィルター条件を変更できることを確認
  it('フィルターを更新できる', () => {
    // ユーザーがタグ「react」「vue」と作成者「user1」を選択した状況をシミュレート
    store.updateFilters({
      tags: ['react', 'vue'],  // タグフィルターに2つ追加
      authors: ['user1']       // 作成者フィルターに1つ追加
    })

    // 設定した値が正しく保存されているかチェック
    expect(store.filters.tags).toEqual(['react', 'vue'])
    expect(store.filters.authors).toEqual(['user1'])
  })

  // 【テスト3】アクティブフィルターの判定が正しく動作することを確認
  it('hasActiveFiltersが正しく計算される', () => {
    // 初期状態では何もフィルターが選択されていない
    expect(store.hasActiveFilters).toBe(false)  // false が正しい
    
    // タグを1つ選択すると、アクティブなフィルターありと判定される
    store.updateFilters({ tags: ['react'] })
    expect(store.hasActiveFilters).toBe(true)   // true に変わる
  })

  // 【テスト4】フィルター条件をすべてクリア（リセット）できることを確認
  it('フィルターをクリアできる', () => {
    // まずフィルターを設定（テスト準備）
    store.updateFilters({ tags: ['react'] })
    expect(store.hasActiveFilters).toBe(true)  // フィルターが設定されている状態

    // フィルターをクリア実行
    store.clearFilters()
    
    // クリア後の状態をチェック
    expect(store.hasActiveFilters).toBe(false) // フィルターなしの状態に戻る
    expect(store.filters.tags).toEqual([])     // タグ選択もクリアされる
  })

  // 【テスト5】APIからの検索結果を正しく保存できることを確認
  it('検索結果を設定できる', () => {
    // APIから返ってきた検索結果のサンプルデータ
    const mockResponse = {
      results: [{ id: '1', title: 'Test' }], // 1件のホワイトボードが見つかった
      total: 1,        // 総件数1件
      page: 1,         // 1ページ目
      pageSize: 10,    // 1ページに10件表示設定
      hasNext: false   // 次のページなし
    }

    // 検索結果をストアに保存
    store.setSearchResults(mockResponse as any)
    
    // 正しく保存されたかチェック
    expect(store.totalResults).toBe(1)                // 総件数が1件
    expect(store.searchResults.length).toBe(1)        // 結果配列に1件格納
  })

  // 【テスト6】ページネーション（ページ移動）機能が正しく動作することを確認
  it('ページネーション状態を管理できる', () => {
    // 2ページ目に移動
    store.setCurrentPage(2)
    expect(store.currentPage).toBe(2)  // 現在ページが2に変わる

    // 1ページあたりの表示件数を20件に変更
    store.setPageSize(20)
    expect(store.pageSize).toBe(20)    // 表示件数が20に変わる
    expect(store.currentPage).toBe(1)  // ページサイズ変更時は1ページ目にリセット
  })
})