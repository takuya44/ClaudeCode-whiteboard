/**
 * AuthorFilter コンポーネントのテストファイル
 * 
 * このファイルでは、作成者による絞り込み検索を行うVueコンポーネント
 * （AuthorFilter.vue）が正しく表示されることをテストしています。
 * 
 * テストする内容：
 * - コンポーネントが期待通りに画面表示される
 * - 「自分のホワイトボード」ボタンが存在する
 * - 必要な要素（ラベル、選択ボックス、説明テキスト）が存在する
 * - アイコン（SVG）が正しく表示される
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AuthorFilter from '../AuthorFilter.vue'

describe('AuthorFilter (Simplified)', () => {
  
  // 【テスト前準備】各テストの実行前に必ず実行される処理
  beforeEach(() => {
    setActivePinia(createPinia())  // Vue状態管理（Pinia）を初期化
  })

  // 【テスト1】コンポーネントが期待した内容で表示されることを確認
  it('コンポーネントが正しくレンダリングされる', () => {
    // AuthorFilterコンポーネントをテスト用に仮想的にマウント（表示）
    const wrapper = mount(AuthorFilter, {
      global: {
        stubs: {
          // Multiselectコンポーネントを偽物に置き換え
          Multiselect: {
            template: '<div data-testid="multiselect" />'  // シンプルなHTMLに置き換え
          }
        }
      }
    })
    
    // ≪表示内容の確認≫
    // ラベル「作成者で絞り込み」が表示されているかチェック
    expect(wrapper.find('label').text()).toBe('作成者で絞り込み')
    
    // 「自分のホワイトボード」というテキストが存在するかチェック
    expect(wrapper.text()).toContain('自分のホワイトボード')
    
    // マルチセレクトボックス（モックの偽物）が存在するかチェック
    expect(wrapper.find('[data-testid="multiselect"]').exists()).toBe(true)
    
    // ヘルプテキスト（OR検索の説明）が表示されているかチェック
    expect(wrapper.text()).toContain('複数選択した場合、いずれかの作成者によるホワイトボードが表示されます')
    
    // テスト終了後のクリーンアップ（メモリ節約）
    wrapper.unmount()
  })

  // 【テスト2】「自分のホワイトボード」ボタンが正しく表示されることを確認
  it('「自分のホワイトボード」ボタンが表示される', () => {
    // AuthorFilterコンポーネントをテスト用に仮想的にマウント（表示）
    const wrapper = mount(AuthorFilter, {
      global: {
        stubs: {
          // Multiselectコンポーネントを偽物に置き換え（true = 完全に隠す）
          Multiselect: true
        }
      }
    })
    
    // ≪ボタン要素の確認≫
    // ページ内の最初のボタン要素を取得
    const myButton = wrapper.find('button')
    
    // ボタンが存在することを確認
    expect(myButton.exists()).toBe(true)
    
    // ボタンのテキストに「自分のホワイトボード」が含まれることを確認
    expect(myButton.text()).toContain('自分のホワイトボード')
    
    // ボタン内にSVGアイコン（人のマークなど）が存在することを確認
    expect(myButton.find('svg').exists()).toBe(true)
    
    // テスト終了後のクリーンアップ（メモリ節約）
    wrapper.unmount()
  })
})