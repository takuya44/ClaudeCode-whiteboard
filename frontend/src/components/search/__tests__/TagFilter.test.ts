/**
 * TagFilter コンポーネントのテストファイル
 * 
 * このファイルでは、タグによる絞り込み検索を行うVueコンポーネント
 * （TagFilter.vue）が正しく表示されることをテストしています。
 * 
 * テストする内容：
 * - コンポーネントが期待通りに画面表示される
 * - 必要な要素（ラベル、選択ボックス、説明テキスト）が存在する
 * - CSSクラスが正しく設定されている
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TagFilter from '../TagFilter.vue'

// 【モック設定】@vueform/multiselect ライブラリの偽物を作成
// 実際の複雑なマルチセレクトボックスの代わりに、シンプルなdivを表示
vi.mock('@vueform/multiselect', () => ({
  default: {
    name: 'MockMultiselect',                        // コンポーネント名
    template: '<div data-testid="multiselect" />',  // シンプルなHTMLに置き換え
    props: ['modelValue', 'options', 'multiple', 'loading', 'disabled']  // 必要な属性だけ定義
  }
}))

describe('TagFilter (Simplified)', () => {
  
  // 【テスト前準備】各テストの実行前に必ず実行される処理
  beforeEach(() => {
    setActivePinia(createPinia())  // Vue状態管理（Pinia）を初期化
  })

  // 【テスト1】コンポーネントが期待した内容で表示されることを確認
  it('コンポーネントが正しくレンダリングされる', () => {
    // TagFilterコンポーネントをテスト用に仮想的にマウント（表示）
    const wrapper = mount(TagFilter)
    
    // ≪表示内容の確認≫
    // ラベル「タグで絞り込み」が表示されているかチェック
    expect(wrapper.find('label').text()).toBe('タグで絞り込み')
    
    // マルチセレクトボックス（モックの偽物）が存在するかチェック
    expect(wrapper.find('[data-testid="multiselect"]').exists()).toBe(true)
    
    // ヘルプテキスト（使い方説明）が表示されているかチェック
    expect(wrapper.text()).toContain('複数選択した場合、すべてのタグを含むホワイトボードが表示されます')
    
    // テスト終了後のクリーンアップ（メモリ節約）
    wrapper.unmount()
  })

  // 【テスト2】CSSクラスが正しく設定されていることを確認
  it('適切なクラスが設定されている', () => {
    // TagFilterコンポーネントをテスト用に仮想的にマウント（表示）
    const wrapper = mount(TagFilter)
    
    // ≪CSSクラスの確認≫
    // メインコンテナに「tag-filter」クラスが設定されているかチェック
    expect(wrapper.find('.tag-filter').exists()).toBe(true)
    
    // マルチセレクトボックスに「multiselect-custom」クラスが設定されているかチェック
    expect(wrapper.find('.multiselect-custom').exists()).toBe(true)
    
    // テスト終了後のクリーンアップ（メモリ節約）
    wrapper.unmount()
  })
})