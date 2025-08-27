// ==================================================
// 【DateRangeFilter.test.ts】日付範囲フィルターコンポーネントのテストファイル
// ==================================================

import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DateRangeFilter from '../DateRangeFilter.vue'
import { useSearchStore } from '../../../stores/search'

// ==================================================
// 【テスト準備】各テスト実行前に初期化を行う
// ==================================================
describe('DateRangeFilter', () => {
  let wrapper: any
  let store: any

  beforeEach(() => {
    // 【Pinia準備】状態管理システムの初期化
    const pinia = createPinia()
    setActivePinia(pinia)
    
    // 【ストア取得】検索用の状態管理を取得
    store = useSearchStore()
    
    // 【コンポーネントマウント】テスト用にDateRangeFilterコンポーネントを準備
    wrapper = mount(DateRangeFilter, {
      global: {
        plugins: [pinia]
      }
    })
  })

  // ==================================================
  // 【テスト1】コンポーネントが正常に表示されることを確認
  // ==================================================
  it('コンポーネントが正常にレンダリングされる', () => {
    // 【確認】DateRangeFilterコンポーネントが画面に表示される
    expect(wrapper.find('.date-range-filter').exists()).toBe(true)
    
    // 【確認】「日付範囲で絞り込み」のタイトルが表示される
    expect(wrapper.text()).toContain('日付範囲で絞り込み')
  })

  // ==================================================
  // 【テスト2】作成日と更新日の切り替えボタンが正常に動作することを確認
  // ==================================================
  it('日付タイプの切り替えが動作する', async () => {
    // 【確認】日付タイプ切り替えボタンが存在する
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThan(0)
    
    // 【確認】「作成日」と「更新日」のテキストが存在する
    expect(wrapper.text()).toContain('作成日')
    expect(wrapper.text()).toContain('更新日')
    
    // 【操作】2番目のボタン（更新日）をクリック
    await buttons[1].trigger('click')
    
    // 【確認】ストアの日付タイプが「updated」に変更される
    expect(store.filters.dateRange.type).toBe('updated')
  })

  // ==================================================
  // 【テスト3】プリセットボタン（今日、過去7日など）が表示されることを確認
  // ==================================================
  it('日付プリセットボタンが表示される', () => {
    // 【確認】「今日」プリセットボタンが存在する
    expect(wrapper.text()).toContain('今日')
    
    // 【確認】「過去7日」プリセットボタンが存在する
    expect(wrapper.text()).toContain('過去7日')
    
    // 【確認】「今月」プリセットボタンが存在する
    expect(wrapper.text()).toContain('今月')
    
    // 【確認】「先月」プリセットボタンが存在する
    expect(wrapper.text()).toContain('先月')
  })

  // ==================================================
  // 【テスト4】開始日と終了日の入力フィールドが存在することを確認
  // ==================================================
  it('開始日と終了日の入力フィールドが表示される', () => {
    // 【確認】「開始日」ラベルが表示される
    expect(wrapper.text()).toContain('開始日')
    
    // 【確認】「終了日」ラベルが表示される
    expect(wrapper.text()).toContain('終了日')
    
    // 【確認】日付入力フィールドが2つ存在する（開始日と終了日）
    const dateInputs = wrapper.findAll('input[type="date"]')
    expect(dateInputs).toHaveLength(2)
  })

  // ==================================================
  // 【テスト5】日付範囲クリアボタンの動作確認
  // ==================================================
  it('日付範囲クリア機能が動作する', async () => {
    // 【事前準備】テスト用に日付範囲を設定
    store.updateFilters({
      dateRange: {
        start: new Date('2024-01-01'),
        end: new Date('2024-01-31'),
        type: 'created'
      }
    })
    
    // 【Vue更新待機】状態変更が画面に反映されるまで待つ
    await wrapper.vm.$nextTick()
    
    // 【確認】「日付範囲をクリア」のテキストが表示される
    expect(wrapper.text()).toContain('日付範囲をクリア')
    
    // 【確認】すべてのボタンを取得してクリアボタンを探す
    const buttons = wrapper.findAll('button')
    const clearButton = buttons.find((button: any) => button.text().includes('日付範囲をクリア'))
    expect(clearButton).toBeDefined()
    
    // 【操作】クリアボタンをクリック
    if (clearButton) {
      await clearButton.trigger('click')
    }
    
    // 【確認】日付範囲がクリアされる
    expect(store.filters.dateRange.start).toBe(null)
    expect(store.filters.dateRange.end).toBe(null)
  })

  // ==================================================
  // 【テスト6】ヘルプテキストが正しく表示されることを確認
  // ==================================================
  it('適切なヘルプテキストが表示される', () => {
    // 【確認】作成日モードでのヘルプテキスト
    expect(wrapper.text()).toContain('作成日を基準に検索します')
    
    // 【日付タイプ変更】更新日モードに切り替え
    store.updateFilters({
      dateRange: {
        start: null,
        end: null,
        type: 'updated'
      }
    })
    
    // 【Vue更新待機】状態変更が画面に反映されるまで待つ
    wrapper.vm.$nextTick().then(() => {
      // 【確認】更新日モードでのヘルプテキスト
      expect(wrapper.text()).toContain('更新日を基準に検索します')
    })
  })
})

// ==================================================
// 【コメント】このテストファイルについて
// ==================================================
/*
このテストファイルでは、DateRangeFilterコンポーネントの基本機能をテストしています：

1. 【画面表示テスト】コンポーネントが正常に表示されるか
2. 【ボタン動作テスト】作成日/更新日の切り替えボタンが動作するか
3. 【プリセット表示テスト】日付プリセットボタンが表示されるか
4. 【入力フィールドテスト】日付入力フィールドが存在するか
5. 【クリア機能テスト】日付範囲のクリア機能が動作するか
6. 【ヘルプテキストテスト】適切な説明文が表示されるか

各テストは独立しており、beforeEachで毎回クリーンな状態から開始されます。
実際の日付入力や複雑なバリデーション機能は、より高度なテストで扱います。
*/