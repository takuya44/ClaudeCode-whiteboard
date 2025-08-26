import { test, expect } from '@playwright/test'

/**
 * 高度な検索機能の主要シナリオE2Eテスト
 * Issue #21 Section 8.3 "主要シナリオテスト" の実装
 * 
 * このテストファイルの目的：
 * - 実際のユーザーが行う検索ワークフローを完全に再現
 * - タグ検索、作成者検索、日付範囲検索、複合検索の主要シナリオをテスト
 * - 検索結果操作（ページネーション、ソート、詳細遷移）を検証
 * - エラーシナリオとユーザビリティを包括的に確認
 */

// Mock data types for test scenarios
interface MockWhiteboard {
  id: number
  title: string
  description: string
  created_at: string
  updated_at: string
  creator: {
    id: number
    username: string
    display_name: string
  }
  tags: string[]
  is_public: boolean
  collaborators_count: number
}

test.describe('Main Search Scenarios', () => {
  test.beforeEach(async ({ page }) => {
    // 認証APIのモック設定
    await page.route('**/api/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            id: 1,
            username: 'testuser',
            email: 'test@example.com'
          }
        })
      })
    })

    // テスト用認証状態の設定（正しいキー名を使用）
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'test-token')
      localStorage.setItem('user', JSON.stringify({
        id: 1,
        username: 'testuser',
        email: 'test@example.com'
      }))
    })
  })

  /**
   * 主要シナリオ1: タグ検索による絞り込み
   * @vueform/multiselect を使用したタグ選択とAND検索の動作確認
   */
  test('Main Scenario 1: Tag-based Search with AND Logic', async ({ page }) => {
    // Mock tags API with realistic data
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [
            { name: 'Vue.js', count: 15 },
            { name: 'React', count: 8 },
            { name: 'TypeScript', count: 12 },
            { name: 'UI/UX', count: 6 },
            { name: 'Planning', count: 10 }
          ]
        })
      })
    })

    // Mock search results for tag-based search
    await page.route('**/api/v1/search/whiteboards', async route => {
      const url = new URL(route.request().url())
      const tags = url.searchParams.get('tags')
      
      if (tags?.includes('Vue.js')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            whiteboards: [
              {
                id: 1,
                title: 'Vue.js Component Architecture',
                description: 'Design patterns for Vue.js components',
                created_at: '2023-12-01T10:00:00Z',
                updated_at: '2023-12-15T14:30:00Z',
                creator: { id: 1, username: 'vue_expert', display_name: 'Vue Expert' },
                tags: ['Vue.js', 'TypeScript', 'Planning'],
                is_public: true,
                collaborators_count: 3
              },
              {
                id: 2,
                title: 'Vue.js State Management',
                description: 'Pinia store patterns and best practices',
                created_at: '2023-11-20T09:15:00Z',
                updated_at: '2023-12-10T16:45:00Z',
                creator: { id: 2, username: 'pinia_dev', display_name: 'Pinia Developer' },
                tags: ['Vue.js', 'Pinia', 'State Management'],
                is_public: false,
                collaborators_count: 2
              }
            ],
            total: 2,
            page: 1,
            per_page: 20
          })
        })
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ whiteboards: [], total: 0, page: 1, per_page: 20 })
        })
      }
    })

    // Navigate to search page
    await page.goto('/app/search')
    
    // ユーザーシナリオ: タグフィルターを使用した検索
    // Step 1: タグフィルターを開く
    await page.waitForSelector('[data-testid="tag-filter"]', { timeout: 10000 })
    await page.click('[data-testid="tag-filter"] .multiselect')
    
    // Step 2: Vue.jsタグを選択
    await page.click('text=Vue.js')
    
    // Step 3: アクティブフィルターの確認
    await expect(page.getByText('タグ: Vue.js')).toBeVisible()
    
    // Step 4: 検索結果の表示確認
    await page.waitForSelector('[data-testid="search-results"]', { timeout: 10000 })
    await expect(page.getByText('検索結果 (2件)')).toBeVisible()
    await expect(page.getByText('Vue.js Component Architecture')).toBeVisible()
    await expect(page.getByText('Vue.js State Management')).toBeVisible()
    
    // Step 5: 複数タグでのAND検索テスト
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=TypeScript')
    
    // AND検索により結果が絞り込まれることを確認
    await expect(page.getByText('タグ: Vue.js')).toBeVisible()
    await expect(page.getByText('タグ: TypeScript')).toBeVisible()
    
    // Step 6: 検索結果のメタデータ確認
    await expect(page.getByText('Vue Expert')).toBeVisible()
    await expect(page.getByText('コラボレーター: 3名')).toBeVisible()
    await expect(page.getByText('公開')).toBeVisible()
  })

  /**
   * 主要シナリオ2: 作成者検索とクイックフィルター
   * 作成者選択、OR検索、「自分のホワイトボード」クイックフィルターの動作確認
   */
  test('Main Scenario 2: Author Search with Quick Filter', async ({ page }) => {
    // Mock authors API
    await page.route('**/api/v1/search/authors', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          authors: [
            { id: 1, username: 'testuser', display_name: 'Test User', whiteboard_count: 12 },
            { id: 2, username: 'john_doe', display_name: 'John Doe', whiteboard_count: 8 },
            { id: 3, username: 'jane_smith', display_name: 'Jane Smith', whiteboard_count: 15 }
          ]
        })
      })
    })

    // Mock search results for author-based search
    await page.route('**/api/v1/search/whiteboards', async route => {
      const url = new URL(route.request().url())
      const authors = url.searchParams.get('authors')
      const myBoards = url.searchParams.get('my_boards')
      
      if (myBoards === 'true') {
        // 自分のホワイトボードのみ
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            whiteboards: [
              {
                id: 3,
                title: 'My Personal Project',
                description: 'Personal brainstorming board',
                created_at: '2023-12-05T08:30:00Z',
                updated_at: '2023-12-15T12:00:00Z',
                creator: { id: 1, username: 'testuser', display_name: 'Test User' },
                tags: ['Personal', 'Ideas'],
                is_public: false,
                collaborators_count: 0
              }
            ],
            total: 1,
            page: 1,
            per_page: 20
          })
        })
      } else if (authors?.includes('john_doe')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            whiteboards: [
              {
                id: 4,
                title: 'John\'s Design System',
                description: 'Comprehensive design system documentation',
                created_at: '2023-11-25T14:15:00Z',
                updated_at: '2023-12-12T10:30:00Z',
                creator: { id: 2, username: 'john_doe', display_name: 'John Doe' },
                tags: ['Design System', 'UI/UX'],
                is_public: true,
                collaborators_count: 5
              }
            ],
            total: 1,
            page: 1,
            per_page: 20
          })
        })
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ whiteboards: [], total: 0, page: 1, per_page: 20 })
        })
      }
    })

    await page.goto('/app/search')
    
    // ユーザーシナリオ: 作成者による検索
    // Step 1: 「自分のホワイトボード」クイックフィルターを使用
    await page.waitForSelector('[data-testid="author-filter"]', { timeout: 10000 })
    await page.click('text=自分のホワイトボード')
    
    // Step 2: アクティブフィルターと結果の確認
    await expect(page.getByText('作成者: 自分のホワイトボード')).toBeVisible()
    await page.waitForSelector('[data-testid="search-results"]', { timeout: 10000 })
    await expect(page.getByText('My Personal Project')).toBeVisible()
    await expect(page.getByText('検索結果 (1件)')).toBeVisible()
    
    // Step 3: フィルターをクリアして個別作成者を選択
    await page.click('button:has-text("クリア")')
    await page.waitForSelector('[data-testid="author-filter"] .multiselect')
    await page.click('[data-testid="author-filter"] .multiselect')
    await page.click('text=John Doe')
    
    // Step 4: OR検索の動作確認
    await expect(page.getByText('作成者: John Doe')).toBeVisible()
    await page.waitForSelector('[data-testid="search-results"]')
    await expect(page.getByText('John\'s Design System')).toBeVisible()
    
    // Step 5: 複数作成者選択でのOR検索
    await page.click('[data-testid="author-filter"] .multiselect')
    await page.click('text=Jane Smith')
    await expect(page.getByText('作成者: John Doe')).toBeVisible()
    await expect(page.getByText('作成者: Jane Smith')).toBeVisible()
  })

  /**
   * 主要シナリオ3: 日付範囲検索とプリセット機能
   * Vue Tailwind Datepicker、プリセットボタン、バリデーションの動作確認
   */
  test('Main Scenario 3: Date Range Search with Presets and Validation', async ({ page }) => {
    // Mock search results for date range search
    await page.route('**/api/v1/search/whiteboards', async route => {
      const url = new URL(route.request().url())
      const startDate = url.searchParams.get('start_date')
      const endDate = url.searchParams.get('end_date')
      
      if (startDate && endDate) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            whiteboards: [
              {
                id: 5,
                title: 'Recent Project Board',
                description: 'Latest project planning board',
                created_at: '2023-12-10T09:00:00Z',
                updated_at: '2023-12-14T15:45:00Z',
                creator: { id: 1, username: 'recent_user', display_name: 'Recent User' },
                tags: ['Recent', 'Project'],
                is_public: true,
                collaborators_count: 2
              }
            ],
            total: 1,
            page: 1,
            per_page: 20
          })
        })
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ whiteboards: [], total: 0, page: 1, per_page: 20 })
        })
      }
    })

    await page.goto('/app/search')
    
    // ユーザーシナリオ: 日付範囲による検索
    // Step 1: プリセットボタンを使用した検索（過去7日間）
    await expect(page.getByText('日付範囲')).toBeVisible()
    await page.click('text=過去7日間')
    
    // Step 2: アクティブフィルターの確認
    await expect(page.getByText('日付範囲:')).toBeVisible()
    
    // Step 3: 検索結果の確認
    await page.waitForSelector('[data-testid="search-results"]', { timeout: 10000 })
    await expect(page.getByText('Recent Project Board')).toBeVisible()
    
    // Step 4: 他のプリセットボタンのテスト
    await page.click('text=過去30日間')
    await expect(page.getByText('日付範囲:')).toBeVisible()
    
    // Step 5: カスタム日付範囲の設定（無効な範囲でのバリデーションテスト）
    await page.click('text=カスタム範囲')
    
    // 終了日が開始日より前の無効な範囲を設定
    await page.fill('[data-testid="start-date"]', '2023-12-15')
    await page.fill('[data-testid="end-date"]', '2023-12-10')
    
    // バリデーションエラーの表示確認
    await expect(page.getByText('終了日は開始日より後に設定してください')).toBeVisible()
    
    // Step 6: 有効な日付範囲での検索
    await page.fill('[data-testid="end-date"]', '2023-12-20')
    await page.click('button:has-text("適用")')
    
    await expect(page.getByText('日付範囲:')).toBeVisible()
  })

  /**
   * 主要シナリオ4: 複合検索とリアルタイム結果更新
   * マルチフィルター組み合わせとリアルタイム更新の動作確認
   */
  test('Main Scenario 4: Complex Multi-filter Search with Real-time Updates', async ({ page }) => {
    // Mock APIs for complex search
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [
            { name: 'Vue.js', count: 10 },
            { name: 'Design', count: 8 }
          ]
        })
      })
    })

    await page.route('**/api/v1/search/authors', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          authors: [
            { id: 1, username: 'designer', display_name: 'UI Designer', whiteboard_count: 6 }
          ]
        })
      })
    })

    // Mock search results that change based on applied filters
    await page.route('**/api/v1/search/whiteboards', async route => {
      const url = new URL(route.request().url())
      const tags = url.searchParams.get('tags')
      const authors = url.searchParams.get('authors')
      const startDate = url.searchParams.get('start_date')
      
      let whiteboards: MockWhiteboard[] = []
      
      // ステップバイステップでフィルターが追加されるごとに結果が変わることをシミュレート
      if (tags && authors && startDate) {
        // 全フィルター適用時（最も絞り込まれた結果）
        whiteboards = [{
          id: 6,
          title: 'Vue.js UI Design Project',
          description: 'Modern UI design with Vue.js components',
          created_at: '2023-12-12T11:30:00Z',
          updated_at: '2023-12-15T16:20:00Z',
          creator: { id: 1, username: 'designer', display_name: 'UI Designer' },
          tags: ['Vue.js', 'Design', 'UI'],
          is_public: true,
          collaborators_count: 4
        }]
      } else if (tags && authors) {
        // タグ + 作成者フィルター
        whiteboards = [{
          id: 6,
          title: 'Vue.js UI Design Project',
          description: 'Modern UI design with Vue.js components',
          created_at: '2023-12-12T11:30:00Z',
          updated_at: '2023-12-15T16:20:00Z',
          creator: { id: 1, username: 'designer', display_name: 'UI Designer' },
          tags: ['Vue.js', 'Design', 'UI'],
          is_public: true,
          collaborators_count: 4
        }, {
          id: 7,
          title: 'Vue.js Design System',
          description: 'Component library documentation',
          created_at: '2023-11-28T14:00:00Z',
          updated_at: '2023-12-08T09:45:00Z',
          creator: { id: 1, username: 'designer', display_name: 'UI Designer' },
          tags: ['Vue.js', 'Design System'],
          is_public: false,
          collaborators_count: 2
        }]
      } else if (tags) {
        // タグフィルターのみ
        whiteboards = Array.from({ length: 5 }, (_, i) => ({
          id: i + 10,
          title: `Vue.js Project ${i + 1}`,
          description: 'Vue.js related project',
          created_at: '2023-12-01T10:00:00Z',
          updated_at: '2023-12-10T15:00:00Z',
          creator: { id: i + 1, username: `user${i + 1}`, display_name: `User ${i + 1}` },
          tags: ['Vue.js'],
          is_public: true,
          collaborators_count: 1
        }))
      }
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          whiteboards,
          total: whiteboards.length,
          page: 1,
          per_page: 20
        })
      })
    })

    await page.goto('/app/search')
    
    // ユーザーシナリオ: 段階的なフィルター適用とリアルタイム更新の確認
    // Step 1: 最初のフィルター（タグ）を適用
    await page.waitForSelector('[data-testid="tag-filter"]', { timeout: 10000 })
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=Vue.js')
    
    // リアルタイム更新: 結果数の変化を確認
    await page.waitForSelector('[data-testid="search-results"]')
    await expect(page.getByText('検索結果 (5件)')).toBeVisible()
    
    // Step 2: 2番目のフィルター（作成者）を追加
    await page.waitForSelector('[data-testid="author-filter"]')
    await page.click('[data-testid="author-filter"] .multiselect')
    await page.click('text=UI Designer')
    
    // リアルタイム更新: 結果がさらに絞り込まれることを確認
    await expect(page.getByText('検索結果 (2件)')).toBeVisible()
    await expect(page.getByText('Vue.js UI Design Project')).toBeVisible()
    await expect(page.getByText('Vue.js Design System')).toBeVisible()
    
    // Step 3: 3番目のフィルター（日付）を追加
    await page.click('text=過去7日間')
    
    // リアルタイム更新: 最終的に最も絞り込まれた結果を確認
    await expect(page.getByText('検索結果 (1件)')).toBeVisible()
    await expect(page.getByText('Vue.js UI Design Project')).toBeVisible()
    
    // Step 4: アクティブフィルターの表示確認
    await expect(page.getByText('タグ: Vue.js')).toBeVisible()
    await expect(page.getByText('作成者: UI Designer')).toBeVisible()
    await expect(page.getByText('日付範囲:')).toBeVisible()
    
    // Step 5: フィルターの個別削除機能テスト
    await page.click('text=タグ: Vue.js [data-testid="remove-filter"]')
    
    // フィルター削除後のリアルタイム更新確認
    await expect(page.getByText('タグ: Vue.js')).not.toBeVisible()
    await expect(page.getByText('作成者: UI Designer')).toBeVisible()
    await expect(page.getByText('日付範囲:')).toBeVisible()
  })

  /**
   * 主要シナリオ5: 検索結果操作とナビゲーション
   * ページネーション、ソート、ホワイトボード詳細遷移の動作確認
   */
  test('Main Scenario 5: Search Results Operations and Navigation', async ({ page }) => {
    // Mock large dataset for pagination testing
    const mockWhiteboards: MockWhiteboard[] = Array.from({ length: 50 }, (_, i) => ({
      id: i + 1,
      title: `Whiteboard ${i + 1}`,
      description: `Description for whiteboard ${i + 1}`,
      created_at: `2023-${String(12 - Math.floor(i / 10)).padStart(2, '0')}-${String((i % 10) + 1).padStart(2, '0')}T10:00:00Z`,
      updated_at: `2023-12-${String((i % 30) + 1).padStart(2, '0')}T15:00:00Z`,
      creator: { id: (i % 5) + 1, username: `user${(i % 5) + 1}`, display_name: `User ${(i % 5) + 1}` },
      tags: [`tag${(i % 3) + 1}`],
      is_public: i % 2 === 0,
      collaborators_count: (i % 5) + 1
    }))

    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [{ name: 'tag1', count: 50 }]
        })
      })
    })

    await page.route('**/api/v1/search/whiteboards', async route => {
      const url = new URL(route.request().url())
      const page_num = parseInt(url.searchParams.get('page') || '1')
      const per_page = parseInt(url.searchParams.get('per_page') || '20')
      const sort_by = url.searchParams.get('sort_by') || 'updated_at'
      const sort_order = url.searchParams.get('sort_order') || 'desc'
      
      // Sort whiteboards based on parameters
      const sortedWhiteboards = [...mockWhiteboards].sort((a, b) => {
        if (sort_by === 'created_at') {
          const aDate = new Date(a.created_at)
          const bDate = new Date(b.created_at)
          return sort_order === 'desc' ? bDate.getTime() - aDate.getTime() : aDate.getTime() - bDate.getTime()
        } else if (sort_by === 'title') {
          return sort_order === 'desc' ? b.title.localeCompare(a.title) : a.title.localeCompare(b.title)
        } else {
          // Default: updated_at
          const aDate = new Date(a.updated_at)
          const bDate = new Date(b.updated_at)
          return sort_order === 'desc' ? bDate.getTime() - aDate.getTime() : aDate.getTime() - bDate.getTime()
        }
      })
      
      // Paginate results
      const start = (page_num - 1) * per_page
      const paginatedWhiteboards = sortedWhiteboards.slice(start, start + per_page)
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          whiteboards: paginatedWhiteboards,
          total: sortedWhiteboards.length,
          page: page_num,
          per_page,
          total_pages: Math.ceil(sortedWhiteboards.length / per_page)
        })
      })
    })

    await page.goto('/app/search')
    
    // ユーザーシナリオ: 検索結果の操作とナビゲーション
    // Step 1: 検索を実行して結果を表示
    await page.waitForSelector('[data-testid="tag-filter"]', { timeout: 10000 })
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=tag1')
    
    await page.waitForSelector('[data-testid="search-results"]')
    await expect(page.getByText('検索結果 (50件)')).toBeVisible()
    
    // Step 2: ソート機能のテスト
    const sortSelect = page.getByRole('combobox', { name: '並び替え:' })
    await expect(sortSelect).toBeVisible()
    
    // 作成日順（古い順）でソート
    await sortSelect.selectOption('created_at_asc')
    
    // ソート後の結果確認
    await page.waitForSelector('text=検索中...')
    await page.waitForSelector('[data-testid="search-results"]')
    await expect(page.getByText('Whiteboard 1')).toBeVisible()
    
    // Step 3: ページネーション機能のテスト
    // ページネーション表示の確認
    await expect(page.getByText('1 / 3')).toBeVisible() // 50件、20件/ページ = 3ページ
    await expect(page.getByRole('button', { name: '次のページ' })).toBeVisible()
    
    // 次のページに移動
    await page.click('button:has-text("次のページ")')
    
    // ページ2の結果確認
    await page.waitForSelector('[data-testid="search-results"]')
    await expect(page.getByText('2 / 3')).toBeVisible()
    await expect(page.getByText('Whiteboard 21')).toBeVisible()
    
    // 前のページに戻る
    await page.click('button:has-text("前のページ")')
    await expect(page.getByText('1 / 3')).toBeVisible()
    
    // Step 4: ホワイトボード詳細への遷移テスト
    await page.click('text=Whiteboard 1')
    
    // 詳細ページへの遷移確認（URLの変化をチェック）
    await expect(page).toHaveURL(/\/app\/whiteboard\/1/)
    
    // Step 5: 検索ページに戻る
    await page.goBack()
    await expect(page).toHaveURL(/\/app\/search/)
    
    // フィルター状態が保持されていることを確認
    await expect(page.getByText('タグ: tag1')).toBeVisible()
    await expect(page.getByText('検索結果 (50件)')).toBeVisible()
  })

  /**
   * 主要シナリオ6: エラーシナリオとユーザビリティ
   * ネットワークエラー、バリデーション、フォールバック動作の確認
   */
  test('Main Scenario 6: Error Scenarios and User Experience', async ({ page }) => {
    await page.goto('/app/search')
    
    // エラーシナリオ1: ネットワークエラー時のフォールバック
    await page.route('**/api/v1/search/tags', async route => {
      await route.abort('failed')
    })
    
    // タグフィルターの読み込みでエラーが発生
    await page.waitForSelector('[data-testid="tag-filter"]', { timeout: 10000 })
    
    // エラー状態の表示確認
    await expect(page.getByText('タグの読み込みに失敗しました')).toBeVisible()
    await expect(page.getByRole('button', { name: '再試行' })).toBeVisible()
    
    // エラーシナリオ2: 検索結果0件時の提案表示
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ tags: [{ name: 'NonExistentTag', count: 0 }] })
      })
    })
    
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ whiteboards: [], total: 0, page: 1, per_page: 20 })
      })
    })
    
    // 再試行ボタンをクリック
    await page.click('button:has-text("再試行")')
    
    // タグフィルターが復旧することを確認
    await page.waitForSelector('[data-testid="tag-filter"] .multiselect')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=NonExistentTag')
    
    // 検索結果0件時の表示確認
    await page.waitForSelector('text=ホワイトボードが見つかりませんでした', { timeout: 10000 })
    await expect(page.getByText('ホワイトボードが見つかりませんでした')).toBeVisible()
    await expect(page.getByText('検索条件を変更してもう一度お試しください')).toBeVisible()
    await expect(page.getByText('以下の方法をお試しください:')).toBeVisible()
    await expect(page.getByText('フィルターを減らす')).toBeVisible()
    await expect(page.getByText('キーワードを変更する')).toBeVisible()
    
    // エラーシナリオ3: 認証エラー時の処理
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Unauthorized' })
      })
    })
    
    // 認証が必要な検索を実行
    await page.click('text=過去7日間')
    
    // 認証エラー時の処理確認
    await page.waitForSelector('text=認証が必要です', { timeout: 10000 })
    await expect(page.getByText('認証が必要です')).toBeVisible()
    await expect(page.getByRole('button', { name: 'ログイン' })).toBeVisible()
  })
})