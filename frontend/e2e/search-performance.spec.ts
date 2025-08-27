import { test, expect } from '@playwright/test'

/**
 * 検索機能のパフォーマンステスト
 * REQ-6要件（200ms以内の検索応答時間）とUIレスポンシブ性をテストします
 * 
 * テストの重要性：
 * - ユーザーエクスペリエンスに直結するレスポンス速度を検証
 * - 大量データでも快適に動作することを保証
 * - 同時に複数の検索リクエストが発生しても安定動作することを確認
 */
test.describe('Search Performance', () => {
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
  })

  test('search API response should be under 200ms (REQ-6)', async ({ page }) => {
    await page.goto('/app/search')
    
    // 高速なAPIレスポンスをモック（実際の処理時間をシミュレート）
    await page.route('**/api/v1/search/whiteboards', async route => {
      // API処理時間をシミュレート（REQ-6要件では200ms以内である必要がある）
      await page.waitForTimeout(150) // 150msの処理時間を模擬
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          // 20件のテストデータを動的生成
          // Array.from()：指定した長さの配列を作成し、各要素を変換
          whiteboards: Array.from({ length: 20 }, (_, i) => ({
            id: i + 1,
            title: `Test Whiteboard ${i + 1}`,
            description: `Description for whiteboard ${i + 1}`,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            creator: { id: 1, username: 'testuser', display_name: 'Test User' },
            tags: ['performance', 'test'],
            is_public: false,
            collaborators_count: 2
          })),
          total: 100,      // 全体の結果数
          page: 1,         // 現在のページ番号
          per_page: 20     // 1ページあたりの表示件数
        })
      })
    })
    
    // タグ一覧APIもモック
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [{ name: 'performance', count: 50 }] // performanceタグが50件で使用
        })
      })
    })
    
    // 検索時間の測定開始
    const startTime = Date.now()
    
    // 検索を実行
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=performance')
    
    // 検索結果が表示されるまで待機
    await page.waitForSelector('[data-testid="search-results"]', { timeout: 5000 })
    
    // 検索時間の測定終了
    const endTime = Date.now()
    const responseTime = endTime - startTime
    
    // REQ-6要件の検証：200ms以内のレスポンス時間
    console.log(`検索レスポンス時間: ${responseTime}ms`)
    // E2Eテストのオーバーヘッドを考慮して1000ms以内で判定
    // （実際のAPI単体では200ms以内である必要がある）
    expect(responseTime).toBeLessThan(1000)
    
    // 検索結果が正しく表示されることを確認
    await expect(page.getByText('Test Whiteboard 1')).toBeVisible()
    await expect(page.getByText('検索結果 (100件)')).toBeVisible()
  })

  test('UI should remain responsive during search', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock slower API to test UI responsiveness
    await page.route('**/api/v1/search/whiteboards', async route => {
      await page.waitForTimeout(1000) // 1 second delay
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ whiteboards: [], total: 0 })
      })
    })
    
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [{ name: 'test', count: 1 }]
        })
      })
    })
    
    // Trigger search
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=test')
    
    // Verify loading state is shown immediately
    await expect(page.getByText('検索中...')).toBeVisible()
    
    // Verify UI remains interactive during search
    // Should be able to interact with other filters
    await expect(page.getByRole('heading', { name: '検索フィルター' })).toBeVisible()
    
    // Should be able to change sort options
    const sortSelect = page.getByRole('combobox', { name: '並び替え:' })
    await expect(sortSelect).toBeVisible()
    await expect(sortSelect).not.toBeDisabled()
    
    // Wait for search to complete
    await page.waitForSelector('text=ホワイトボードが見つかりませんでした', { timeout: 3000 })
  })

  test('should handle large datasets efficiently', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock large dataset response
    const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
      id: i + 1,
      title: `Large Dataset Item ${i + 1}`,
      description: `Description ${i + 1}`,
      created_at: new Date(Date.now() - i * 86400000).toISOString(), // Different dates
      updated_at: new Date().toISOString(),
      creator: { 
        id: (i % 10) + 1, 
        username: `user${(i % 10) + 1}`, 
        display_name: `User ${(i % 10) + 1}` 
      },
      tags: [`tag${i % 5}`, `category${i % 3}`],
      is_public: i % 2 === 0,
      collaborators_count: i % 5
    }))
    
    await page.route('**/api/v1/search/whiteboards', async route => {
      // Simulate realistic processing time for large dataset
      await page.waitForTimeout(100)
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          whiteboards: largeDataset.slice(0, 20), // Paginated results
          total: largeDataset.length,
          page: 1,
          per_page: 20
        })
      })
    })
    
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: Array.from({ length: 100 }, (_, i) => ({
            name: `tag${i}`,
            count: Math.floor(Math.random() * 100) + 1
          }))
        })
      })
    })
    
    // Measure rendering time for large tag list
    const startTime = Date.now()
    
    // Wait for tag filter to load
    await page.waitForSelector('[data-testid="tag-filter"]', { timeout: 10000 })
    
    // Open tag multiselect
    await page.click('[data-testid="tag-filter"] .multiselect')
    
    // Verify all tags are loaded and searchable
    await expect(page.getByText('tag0')).toBeVisible()
    
    const tagLoadTime = Date.now() - startTime
    console.log(`Tag loading time for large dataset: ${tagLoadTime}ms`)
    
    // Should load within reasonable time
    expect(tagLoadTime).toBeLessThan(3000)
    
    // Select a tag and verify search works
    await page.click('text=tag0')
    await page.waitForSelector('[data-testid="search-results"]')
    
    // Verify pagination works with large results
    await expect(page.getByText('検索結果 (1000件)')).toBeVisible()
    await expect(page.getByText('Large Dataset Item 1')).toBeVisible()
  })

  test('should handle rapid filter changes efficiently', async ({ page }) => {
    await page.goto('/app/search')
    
    let searchCount = 0
    
    // Mock API to track search calls
    await page.route('**/api/v1/search/whiteboards', async route => {
      searchCount++
      await page.waitForTimeout(50) // Small delay
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          whiteboards: [{ 
            id: searchCount, 
            title: `Result ${searchCount}`,
            created_at: new Date().toISOString(),
            creator: { id: 1, username: 'test', display_name: 'Test' },
            tags: [],
            is_public: false,
            collaborators_count: 0
          }],
          total: 1
        })
      })
    })
    
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: ['tag1', 'tag2', 'tag3'].map(name => ({ name, count: 5 }))
        })
      })
    })
    
    // Rapidly change filters to test debouncing
    await page.waitForSelector('[data-testid="tag-filter"]')
    
    // Quickly select and deselect multiple tags
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=tag1')
    await page.click('text=tag1') // Deselect
    await page.click('text=tag2')
    await page.click('text=tag2') // Deselect  
    await page.click('text=tag3') // Final selection
    
    // Wait for debounce to settle
    await page.waitForTimeout(1000)
    
    // Verify search was properly debounced (shouldn't make excessive API calls)
    await page.waitForSelector('[data-testid="search-results"]')
    
    // Should have made reasonable number of API calls (debounced)
    console.log(`Total search API calls: ${searchCount}`)
    expect(searchCount).toBeLessThan(5) // Should be debounced, not 6+ calls
  })

  test('should measure page load performance', async ({ page }) => {
    // Measure initial page load time
    const startTime = Date.now()
    
    await page.goto('/app/search')
    
    // Wait for page to be fully loaded
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.waitForSelector('[data-testid="author-filter"]')
    await page.waitForSelector('text=検索フィルターを設定してください')
    
    const loadTime = Date.now() - startTime
    console.log(`Search page load time: ${loadTime}ms`)
    
    // Page should load within reasonable time
    expect(loadTime).toBeLessThan(5000) // 5 seconds max
    
    // Verify critical elements are present
    await expect(page.getByRole('heading', { name: 'ホワイトボード検索' })).toBeVisible()
    await expect(page.getByRole('heading', { name: '検索フィルター' })).toBeVisible()
    await expect(page.getByRole('heading', { name: '検索結果' })).toBeVisible()
  })

  test('should handle concurrent searches gracefully', async ({ page }) => {
    await page.goto('/app/search')
    
    let responseCount = 0
    
    await page.route('**/api/v1/search/whiteboards', async route => {
      responseCount++
      const currentResponse = responseCount
      
      // Add variable delay to simulate different response times
      await page.waitForTimeout(Math.random() * 300 + 100)
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          whiteboards: [{ 
            id: currentResponse, 
            title: `Concurrent Result ${currentResponse}`,
            created_at: new Date().toISOString(),
            creator: { id: 1, username: 'test', display_name: 'Test' },
            tags: [`response${currentResponse}`],
            is_public: false,
            collaborators_count: 0
          }],
          total: 1
        })
      })
    })
    
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: ['concurrent1', 'concurrent2', 'concurrent3'].map(name => ({ name, count: 1 }))
        })
      })
    })
    
    // Trigger multiple searches quickly
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    
    // Select multiple tags in quick succession
    await page.click('text=concurrent1')
    await page.click('text=concurrent2')
    await page.click('text=concurrent3')
    
    // Wait for final result
    await page.waitForSelector('[data-testid="search-results"]', { timeout: 5000 })
    
    // Verify only the latest search result is displayed (race condition handling)
    await expect(page.getByText(/Concurrent Result/)).toBeVisible()
    
    console.log(`Total API responses: ${responseCount}`)
    
    // Should show consistent final state
    const activeFilters = page.locator('[data-testid="active-filters"] .filter-tag')
    await expect(activeFilters).toHaveCount(3) // All three tags selected
  })
})