import { test, expect } from '@playwright/test'

/**
 * 検索ワークフローのE2Eテスト
 * ナビゲーション、フィルター、検索結果表示などの主要機能をテストします
 * 
 * このテストファイルの目的：
 * - 検索ページへの遷移が正しく動作することを確認
 * - タグ、作成者、日付範囲フィルターが期待通りに動作することを検証
 * - 複数フィルターを組み合わせた検索が正しく機能することをテスト
 * - エラー状態や結果なし状態の表示を確認
 */
test.describe('Search Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // テスト用の認証状態をモック（偽装）設定
    // なぜモックするか：実際のログイン処理を毎回行うとテストが重くなるため
    await page.addInitScript(() => {
      // ローカルストレージに認証トークンとユーザー情報を設定
      localStorage.setItem('auth-token', 'test-token')
      localStorage.setItem('user', JSON.stringify({
        id: 1,
        username: 'testuser',
        email: 'test@example.com'
      }))
    })
  })

  test('should navigate to search page and display initial state', async ({ page }) => {
    // 検索ページに移動
    await page.goto('/app/search')
    
    // SEO対策：ページタイトルが正しく設定されているかチェック
    // ブラウザのタブに表示される文字列を確認
    await expect(page).toHaveTitle(/ホワイトボード検索/)
    
    // ページヘッダーの表示確認
    // getByRole('heading')：見出し要素（h1, h2など）を取得
    await expect(page.getByRole('heading', { name: 'ホワイトボード検索' })).toBeVisible()
    await expect(page.getByText('タグ、作成者、日付範囲で絞り込んでホワイトボードを検索')).toBeVisible()
    
    // 検索フィルターサイドバーの表示確認
    await expect(page.getByRole('heading', { name: '検索フィルター' })).toBeVisible()
    
    // 初期状態（フィルター未設定時）のメッセージ表示確認
    // ユーザーガイダンスとして表示される説明文をチェック
    await expect(page.getByText('検索フィルターを設定してください')).toBeVisible()
    await expect(page.getByText('左側のフィルターを使用してホワイトボードを検索')).toBeVisible()
  })

  test('should display search results header with count', async ({ page }) => {
    await page.goto('/app/search')
    
    // Check search results header
    await expect(page.getByRole('heading', { name: '検索結果' })).toBeVisible()
    
    // Check sort dropdown is present
    await expect(page.getByRole('combobox', { name: '並び替え:' })).toBeVisible()
    await expect(page.getByRole('option', { name: '更新日（新しい順）' })).toBeVisible()
  })

  test('should handle tag filter interactions', async ({ page }) => {
    await page.goto('/app/search')
    
    // APIレスポンスをモック（偽装）
    // 実際のサーバーからデータを取得せず、テスト用のデータを返すように設定
    // これにより、テストが外部環境に依存せず安定して実行できます
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200, // HTTP成功ステータス
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [
            { name: 'Vue.js', count: 5 },    // Vue.jsタグが5個のホワイトボードで使用
            { name: 'React', count: 3 },     // Reactタグが3個で使用
            { name: 'TypeScript', count: 8 } // TypeScriptタグが8個で使用
          ]
        })
      })
    })
    
    // タグフィルターが読み込まれるまで待機
    // data-testid="tag-filter"：テスト用に設定した要素識別子
    await page.waitForSelector('[data-testid="tag-filter"]', { timeout: 10000 })
    
    // タグフィルターをクリックしてドロップダウンを開く
    // .multiselect：複数選択可能なドロップダウンのCSSクラス
    await page.click('[data-testid="tag-filter"] .multiselect')
    
    // Vue.jsタグを選択
    // text=Vue.js：「Vue.js」というテキストを持つ要素を探してクリック
    await page.click('text=Vue.js')
    
    // アクティブフィルター（選択中のフィルター）が表示されることを確認
    await expect(page.getByText('タグ: Vue.js')).toBeVisible()
    
    // 検索が開始されたことを確認（ローディング状態の表示）
    await expect(page.getByText('検索中...')).toBeVisible()
  })

  test('should handle author filter interactions', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock available authors API response
    await page.route('**/api/v1/search/authors', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          authors: [
            { id: 1, username: 'john_doe', display_name: 'John Doe', whiteboard_count: 12 },
            { id: 2, username: 'jane_smith', display_name: 'Jane Smith', whiteboard_count: 8 }
          ]
        })
      })
    })
    
    // Wait for author filter to be loaded
    await page.waitForSelector('[data-testid="author-filter"]', { timeout: 10000 })
    
    // Click on author filter to open multiselect
    await page.click('[data-testid="author-filter"] .multiselect')
    
    // Select an author
    await page.click('text=John Doe')
    
    // Verify active filter is displayed
    await expect(page.getByText('作成者: John Doe')).toBeVisible()
  })

  test('should handle date range filter interactions', async ({ page }) => {
    await page.goto('/app/search')
    
    // Find and interact with date range filter
    await expect(page.getByText('日付範囲')).toBeVisible()
    
    // Click on date range preset (last 7 days)
    await page.click('text=過去7日間')
    
    // Verify active filter is displayed
    await expect(page.getByText('日付範囲:')).toBeVisible()
  })

  test('should perform complex multi-filter search', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock APIs
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [{ name: 'Vue.js', count: 5 }]
        })
      })
    })
    
    await page.route('**/api/v1/search/authors', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          authors: [{ id: 1, username: 'john_doe', display_name: 'John Doe', whiteboard_count: 12 }]
        })
      })
    })
    
    // Mock search results
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          whiteboards: [
            {
              id: 1,
              title: 'Vue.js Project Planning',
              description: 'Planning board for Vue.js project',
              created_at: '2023-12-01T10:00:00Z',
              updated_at: '2023-12-15T14:30:00Z',
              creator: { id: 1, username: 'john_doe', display_name: 'John Doe' },
              tags: ['Vue.js', 'Planning'],
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
    
    // Apply multiple filters
    // 1. Tag filter
    await page.waitForSelector('[data-testid="tag-filter"]', { timeout: 10000 })
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=Vue.js')
    
    // 2. Author filter  
    await page.waitForSelector('[data-testid="author-filter"]', { timeout: 10000 })
    await page.click('[data-testid="author-filter"] .multiselect')
    await page.click('text=John Doe')
    
    // 3. Date range filter
    await page.click('text=過去7日間')
    
    // Wait for search results
    await page.waitForSelector('[data-testid="search-results"]', { timeout: 10000 })
    
    // Verify multiple active filters are displayed
    await expect(page.getByText('タグ: Vue.js')).toBeVisible()
    await expect(page.getByText('作成者: John Doe')).toBeVisible()
    await expect(page.getByText('日付範囲:')).toBeVisible()
    
    // Verify search results are displayed
    await expect(page.getByText('Vue.js Project Planning')).toBeVisible()
    await expect(page.getByText('検索結果 (1件)')).toBeVisible()
  })

  test('should handle sort functionality', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock search with results to enable sorting
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ tags: [{ name: 'Test', count: 1 }] })
      })
    })
    
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          whiteboards: [{ id: 1, title: 'Test Board', created_at: '2023-12-01T10:00:00Z' }],
          total: 1
        })
      })
    })
    
    // Apply a filter to trigger search
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=Test')
    
    // Wait for results
    await page.waitForSelector('[data-testid="search-results"]')
    
    // Test sort dropdown
    const sortSelect = page.getByRole('combobox', { name: '並び替え:' })
    await expect(sortSelect).toBeVisible()
    
    // Change sort order
    await sortSelect.selectOption('created_at_asc')
    
    // Verify sort change triggers new search (loading state)
    await expect(page.getByText('検索中...')).toBeVisible()
  })

  test('should display error state gracefully', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock API error
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      })
    })
    
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Search service unavailable' })
      })
    })
    
    // Try to perform a search that will fail
    await page.click('text=過去7日間')
    
    // Wait for error state
    await page.waitForSelector('text=エラーが発生しました', { timeout: 10000 })
    
    // Verify error message and retry button
    await expect(page.getByText('エラーが発生しました')).toBeVisible()
    await expect(page.getByRole('button', { name: '再試行' })).toBeVisible()
    
    // Test retry functionality
    await page.click('button:has-text("再試行")')
    await expect(page.getByText('検索中...')).toBeVisible()
  })

  test('should display no results state', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock empty search results
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
        body: JSON.stringify({
          whiteboards: [],
          total: 0
        })
      })
    })
    
    // Apply filter to trigger search
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=NonExistentTag')
    
    // Wait for and verify no results state
    await page.waitForSelector('text=ホワイトボードが見つかりませんでした', { timeout: 10000 })
    await expect(page.getByText('ホワイトボードが見つかりませんでした')).toBeVisible()
    await expect(page.getByText('検索条件を変更してもう一度お試しください')).toBeVisible()
  })

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/app/search')
    
    // Verify mobile layout
    await expect(page.getByRole('heading', { name: 'ホワイトボード検索' })).toBeVisible()
    
    // Verify filters are still accessible on mobile
    await expect(page.getByRole('heading', { name: '検索フィルター' })).toBeVisible()
    
    // Check that sort dropdown is still functional
    await expect(page.getByRole('combobox', { name: '並び替え:' })).toBeVisible()
  })
})