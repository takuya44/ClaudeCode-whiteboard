import { test, expect } from '@playwright/test'

/**
 * 検索コンポーネント個別機能のE2Eテスト
 * 各フィルターコンポーネントとそのUI動作を詳細にテストします
 * 
 * コンポーネントレベルテストの目的：
 * - 個々のフィルター（タグ、作成者、日付範囲）が正しく動作することを確認
 * - ユーザーインタラクション（クリック、キーボード操作）への適切な反応をチェック
 * - アクセシビリティ（障害者対応）機能が正しく実装されているかを検証
 * - レスポンシブデザインが異なる画面サイズで正常に動作することを保証
 */
test.describe('Search Components', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication state
    await page.addInitScript(() => {
      localStorage.setItem('auth-token', 'test-token')
      localStorage.setItem('user', JSON.stringify({
        id: 1,
        username: 'testuser',
        email: 'test@example.com'
      }))
    })
    
    // Mock basic API responses
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [
            { name: 'Vue.js', count: 15 },
            { name: 'React', count: 8 },
            { name: 'TypeScript', count: 12 },
            { name: 'JavaScript', count: 20 }
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
            { id: 1, username: 'john_doe', display_name: 'John Doe', whiteboard_count: 25 },
            { id: 2, username: 'jane_smith', display_name: 'Jane Smith', whiteboard_count: 18 },
            { id: 3, username: 'alice_jones', display_name: 'Alice Jones', whiteboard_count: 12 }
          ]
        })
      })
    })
    
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          whiteboards: [
            {
              id: 1,
              title: 'Sample Whiteboard',
              description: 'A test whiteboard',
              created_at: '2023-12-01T10:00:00Z',
              updated_at: '2023-12-15T14:30:00Z',
              creator: { id: 1, username: 'john_doe', display_name: 'John Doe' },
              tags: ['Vue.js', 'TypeScript'],
              is_public: false,
              collaborators_count: 3
            }
          ],
          total: 1,
          page: 1,
          per_page: 20
        })
      })
    })
  })

  test('TagFilter component functionality', async ({ page }) => {
    await page.goto('/app/search')
    
    // タグフィルターコンポーネントの読み込み完了まで待機
    await page.waitForSelector('[data-testid="tag-filter"]')
    
    // タグフィルターのヘッダーが正しく表示されることを確認
    await expect(page.getByText('タグで絞り込み')).toBeVisible()
    
    // マルチセレクトドロップダウンを開く
    await page.click('[data-testid="tag-filter"] .multiselect')
    
    // 全てのタグが使用回数と共に表示されることを確認
    // (15)、(8)などの数字は、そのタグが使われているホワイトボードの数
    await expect(page.getByText('Vue.js (15)')).toBeVisible()
    await expect(page.getByText('React (8)')).toBeVisible()
    await expect(page.getByText('TypeScript (12)')).toBeVisible()
    await expect(page.getByText('JavaScript (20)')).toBeVisible()
    
    // 複数のタグを選択
    await page.click('text=Vue.js')
    await page.click('text=TypeScript')
    
    // 選択されたタグが表示されることを確認
    await expect(page.getByText('Vue.js')).toBeVisible()
    await expect(page.getByText('TypeScript')).toBeVisible()
    
    // アクティブフィルターに選択したタグが表示されることを確認
    await expect(page.getByText('タグ: Vue.js, TypeScript')).toBeVisible()
    
    // タグの選択解除機能をテスト
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=Vue.js') // Vue.jsを選択解除
    
    // Vue.jsが削除され、TypeScriptのみが残ることを確認
    await expect(page.getByText('タグ: TypeScript')).toBeVisible()
  })

  test('AuthorFilter component functionality', async ({ page }) => {
    await page.goto('/app/search')
    
    // Wait for author filter to load
    await page.waitForSelector('[data-testid="author-filter"]')
    
    // Verify author filter header
    await expect(page.getByText('作成者で絞り込み')).toBeVisible()
    
    // Test "自分のホワイトボード" quick filter
    await page.click('text=自分のホワイトボード')
    await expect(page.getByText('作成者: testuser')).toBeVisible()
    
    // Clear and test multiselect
    await page.click('text=クリア')
    
    // Open multiselect dropdown
    await page.click('[data-testid="author-filter"] .multiselect')
    
    // Verify authors are displayed with whiteboard counts
    await expect(page.getByText('John Doe (25個のホワイトボード)')).toBeVisible()
    await expect(page.getByText('Jane Smith (18個のホワイトボード)')).toBeVisible()
    await expect(page.getByText('Alice Jones (12個のホワイトボード)')).toBeVisible()
    
    // Select multiple authors
    await page.click('text=John Doe')
    await page.click('text=Jane Smith')
    
    // Verify active filters
    await expect(page.getByText('作成者: John Doe, Jane Smith')).toBeVisible()
  })

  test('DateRangeFilter component functionality', async ({ page }) => {
    await page.goto('/app/search')
    
    // Verify date range filter header
    await expect(page.getByText('日付範囲で絞り込み')).toBeVisible()
    
    // Test preset buttons
    await expect(page.getByRole('button', { name: '過去7日間' })).toBeVisible()
    await expect(page.getByRole('button', { name: '過去30日間' })).toBeVisible()
    await expect(page.getByRole('button', { name: '過去90日間' })).toBeVisible()
    
    // Click on preset
    await page.click('text=過去7日間')
    
    // Verify active filter is displayed
    await expect(page.getByText(/日付範囲: \d{4}-\d{2}-\d{2} 〜 \d{4}-\d{2}-\d{2}/)).toBeVisible()
    
    // Test custom date range
    await page.click('text=カスタム期間')
    
    // Verify custom date inputs are visible
    await expect(page.locator('[data-testid="start-date-input"]')).toBeVisible()
    await expect(page.locator('[data-testid="end-date-input"]')).toBeVisible()
    
    // Set custom dates
    await page.fill('[data-testid="start-date-input"]', '2023-12-01')
    await page.fill('[data-testid="end-date-input"]', '2023-12-31')
    
    // Apply custom date range
    await page.click('text=適用')
    
    // Verify custom date range is active
    await expect(page.getByText('日付範囲: 2023-12-01 〜 2023-12-31')).toBeVisible()
  })

  test('ActiveFilters component functionality', async ({ page }) => {
    await page.goto('/app/search')
    
    // Apply multiple filters
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=Vue.js')
    
    await page.waitForSelector('[data-testid="author-filter"]')
    await page.click('text=自分のホワイトボード')
    
    await page.click('text=過去7日間')
    
    // Wait for active filters to appear
    await page.waitForSelector('[data-testid="active-filters"]')
    
    // Verify all active filters are displayed
    await expect(page.getByText('タグ: Vue.js')).toBeVisible()
    await expect(page.getByText('作成者: testuser')).toBeVisible()
    await expect(page.getByText(/日付範囲:/)).toBeVisible()
    
    // Test individual filter removal
    await page.click('[data-testid="remove-tag-filter"]')
    await expect(page.getByText('タグ: Vue.js')).not.toBeVisible()
    
    // Test clear all filters
    await page.click('text=全てクリア')
    
    // Verify all filters are cleared
    await expect(page.getByText('作成者: testuser')).not.toBeVisible()
    await expect(page.getByText(/日付範囲:/)).not.toBeVisible()
    
    // Verify empty state is shown again
    await expect(page.getByText('検索フィルターを設定してください')).toBeVisible()
  })

  test('SearchResults component functionality', async ({ page }) => {
    await page.goto('/app/search')
    
    // Apply a filter to get results
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=Vue.js')
    
    // Wait for search results
    await page.waitForSelector('[data-testid="search-results"]')
    
    // Verify results header
    await expect(page.getByText('検索結果 (1件)')).toBeVisible()
    
    // Verify result card is displayed
    await expect(page.getByText('Sample Whiteboard')).toBeVisible()
    await expect(page.getByText('A test whiteboard')).toBeVisible()
    await expect(page.getByText('John Doe')).toBeVisible()
    
    // Verify tags are displayed on result card
    await expect(page.getByText('Vue.js')).toBeVisible()
    await expect(page.getByText('TypeScript')).toBeVisible()
    
    // Verify metadata
    await expect(page.getByText('3人のコラボレーター')).toBeVisible()
    await expect(page.getByText(/\d{4}-\d{2}-\d{2}/)).toBeVisible() // Date format
    
    // Test result card click (navigation)
    await page.click('[data-testid="result-card-1"]')
    
    // Should navigate to whiteboard view
    await expect(page).toHaveURL(/\/app\/whiteboard\/1/)
  })

  test('Sort functionality in results', async ({ page }) => {
    await page.goto('/app/search')
    
    // Apply filter to get results
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=Vue.js')
    
    // Wait for results
    await page.waitForSelector('[data-testid="search-results"]')
    
    // Test sort dropdown
    const sortSelect = page.getByRole('combobox', { name: '並び替え:' })
    await expect(sortSelect).toBeVisible()
    
    // Verify default sort option
    await expect(sortSelect).toHaveValue('updated_at_desc')
    
    // Change sort order
    await sortSelect.selectOption('title_asc')
    
    // Verify loading state appears
    await expect(page.getByText('検索中...')).toBeVisible()
    
    // Wait for results to reload
    await page.waitForSelector('[data-testid="search-results"]')
    
    // Verify sort selection is maintained
    await expect(sortSelect).toHaveValue('title_asc')
  })

  test('Pagination functionality', async ({ page }) => {
    // Mock response with pagination
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          whiteboards: Array.from({ length: 20 }, (_, i) => ({
            id: i + 1,
            title: `Paginated Result ${i + 1}`,
            description: `Description ${i + 1}`,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            creator: { id: 1, username: 'test', display_name: 'Test User' },
            tags: ['pagination'],
            is_public: false,
            collaborators_count: 1
          })),
          total: 100, // Total results across all pages
          page: 1,
          per_page: 20,
          total_pages: 5
        })
      })
    })
    
    await page.goto('/app/search')
    
    // Trigger search
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=Vue.js')
    
    // Wait for paginated results
    await page.waitForSelector('[data-testid="search-results"]')
    
    // Verify pagination info
    await expect(page.getByText('検索結果 (100件)')).toBeVisible()
    await expect(page.getByText('1-20件を表示')).toBeVisible()
    
    // Verify pagination controls
    await expect(page.getByRole('button', { name: '次のページ' })).toBeVisible()
    await expect(page.getByRole('button', { name: '前のページ' })).toBeDisabled()
    
    // Test pagination navigation
    await page.click('text=次のページ')
    
    // Should show loading state during page change
    await expect(page.getByText('検索中...')).toBeVisible()
  })

  test('Keyboard navigation and accessibility', async ({ page }) => {
    await page.goto('/app/search')
    
    // Test keyboard navigation in tag filter
    await page.waitForSelector('[data-testid="tag-filter"]')
    
    // Focus on tag filter
    await page.focus('[data-testid="tag-filter"] .multiselect')
    
    // Press Enter to open dropdown
    await page.keyboard.press('Enter')
    
    // Use arrow keys to navigate options
    await page.keyboard.press('ArrowDown')
    await page.keyboard.press('Enter') // Select first option
    
    // Verify selection worked
    await expect(page.getByText('タグ:')).toBeVisible()
    
    // Test Escape to close dropdowns
    await page.keyboard.press('Escape')
    
    // Verify ARIA labels and roles
    await expect(page.locator('[role="combobox"]')).toBeVisible()
    await expect(page.locator('[aria-label="検索フィルター"]')).toBeVisible()
  })
})