/**
 * 検索API クライアントのテストファイル
 * 
 * このファイルでは、フロントエンドからバックエンドサーバーへの
 * 検索機能のAPI呼び出しが正しく動作することをテストしています。
 * 
 * テストする機能：
 * - ホワイトボード検索API（searchWhiteboards）
 * - 利用可能なタグ一覧取得API（getAvailableTags）
 * - 利用可能な作成者一覧取得API（getAvailableAuthors）
 */

import { describe, it, expect, vi } from 'vitest'
import { searchAPI } from '../search'

// 【モック設定】axios ライブラリ（HTTP通信）の偽物を作成
// 実際のサーバー通信をせずに、テスト用の決まった値を返すようにする
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      // POST リクエスト（検索実行）の偽物
      post: vi.fn().mockResolvedValue({
        data: {
          results: [],        // 検索結果：空配列
          total: 0,          // 総件数：0件
          page: 1,           // 現在ページ：1ページ目
          page_size: 10,     // ページサイズ：10件表示
          has_next: false    // 次ページの有無：なし
        }
      }),
      // GET リクエスト（一覧取得）の偽物
      get: vi.fn().mockResolvedValue({ data: [] }),  // 空配列を返す
      
      // HTTP通信の設定機能（認証トークン追加など）の偽物
      interceptors: {
        request: { use: vi.fn() },   // リクエスト時の処理
        response: { use: vi.fn() }   // レスポンス時の処理
      }
    }))
  }
}))

// 【モック設定】ブラウザのローカルストレージ（認証トークン保存場所）の偽物
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: vi.fn(),     // データ取得の偽物
    setItem: vi.fn(),     // データ保存の偽物
    removeItem: vi.fn()   // データ削除の偽物
  }
})

// 【モック設定】console.log と console.error の偽物（ログ出力を抑制）
vi.spyOn(console, 'log').mockImplementation(() => {})    // ログ出力を無効化
vi.spyOn(console, 'error').mockImplementation(() => {})  // エラー出力を無効化

describe('Search API (Simplified)', () => {
  
  // 【テスト1】ホワイトボード検索APIが正しく動作することを確認
  it('searchWhiteboards が正しく動作する', async () => {
    // ≪検索パラメータの準備≫
    // ユーザーが「reactタグ」「user1作成者」で検索する状況をシミュレート
    const params = {
      tags: ['react'],                    // 選択されたタグ
      authors: ['user1'],                 // 選択された作成者
      dateRange: null,                    // 日付範囲指定なし
      sortBy: 'updated_at' as const,      // 更新日順でソート
      sortOrder: 'desc' as const,         // 降順（新しい順）
      page: 1,                           // 1ページ目
      pageSize: 10                       // 1ページに10件表示
    }

    // ≪API呼び出し実行≫
    // 検索APIを実際に呼び出し（モックなので偽の結果が返る）
    const result = await searchAPI.searchWhiteboards(params)
    
    // ≪返り値の形式チェック≫
    // APIから返ってくるデータが期待した構造を持っているか確認
    expect(result).toHaveProperty('results')   // 検索結果配列
    expect(result).toHaveProperty('total')     // 総件数
    expect(result).toHaveProperty('page')      // 現在ページ
    expect(result).toHaveProperty('pageSize')  // ページサイズ
  })

  // 【テスト2】利用可能なタグ一覧取得APIが正しく動作することを確認
  it('getAvailableTags が正しく動作する', async () => {
    // ≪API呼び出し実行≫
    // タグ一覧取得APIを呼び出し（モックなので空配列が返る）
    const result = await searchAPI.getAvailableTags()
    
    // ≪返り値の型チェック≫
    // 結果が配列形式（Tag[]）で返ってくることを確認
    expect(Array.isArray(result)).toBe(true)
  })

  // 【テスト3】利用可能な作成者一覧取得APIが正しく動作することを確認
  it('getAvailableAuthors が正しく動作する', async () => {
    // ≪API呼び出し実行≫
    // 作成者一覧取得APIを呼び出し（モックなので空配列が返る）
    const result = await searchAPI.getAvailableAuthors()
    
    // ≪返り値の型チェック≫
    // 結果が配列形式（User[]）で返ってくることを確認
    expect(Array.isArray(result)).toBe(true)
  })
})