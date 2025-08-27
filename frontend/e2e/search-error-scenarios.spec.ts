import { test, expect } from '@playwright/test'

/**
 * 検索機能のエラーシナリオとエッジケーステスト
 * ネットワークエラー、バリデーションエラー、フォールバック動作をテストします
 * 
 * エラーテストの重要性：
 * - 実際の運用環境で発生しうる問題への対処を確認
 * - ユーザーにとって分かりやすいエラーメッセージが表示されるかチェック
 * - システムが予期しないエラーで完全に停止しないことを保証
 * - 復旧操作（リトライなど）が適切に動作することを検証
 */
test.describe('Search Error Scenarios', () => {
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

  test('should handle network errors gracefully', async ({ page }) => {
    await page.goto('/app/search')
    
    // ネットワークエラーをシミュレート
    // route.abort('failed')：APIリクエストを失敗状態にする
    // 実際のサーバーダウンやネットワーク切断時の動作を模擬
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.abort('failed') // リクエストを強制失敗させる
    })
    
    // タグAPIは正常に動作するようにモック（検索を実行できるようにするため）
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [{ name: 'TestTag', count: 1 }]
        })
      })
    })
    
    // フィルターを適用して検索を実行（これがネットワークエラーを引き起こす）
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=TestTag')
    
    // ネットワークエラーが適切に処理されることを確認
    // ユーザーにとって分かりやすいエラーメッセージが表示される
    await page.waitForSelector('text=エラーが発生しました', { timeout: 10000 })
    await expect(page.getByText('エラーが発生しました')).toBeVisible()
    
    // 再試行ボタンが表示され、機能することを確認
    await expect(page.getByRole('button', { name: '再試行' })).toBeVisible()
    
    // 再試行機能のテスト（再度検索を試みる）
    await page.click('button:has-text("再試行")')
    await expect(page.getByText('検索中...')).toBeVisible()
  })

  test('should handle API timeout errors', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock slow API response (timeout)
    await page.route('**/api/v1/search/whiteboards', async route => {
      // Delay for longer than expected timeout
      await page.waitForTimeout(30000) // 30 seconds delay
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
          tags: [{ name: 'TestTag', count: 1 }]
        })
      })
    })
    
    // Trigger search
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=TestTag')
    
    // Should show error after timeout
    await expect(page.getByText('エラーが発生しました')).toBeVisible({ timeout: 35000 })
  })

  test('should validate date range inputs', async ({ page }) => {
    await page.goto('/app/search')
    
    // Wait for the page to load
    await page.waitForSelector('[data-testid="date-range-filter"]')
    
    // Find custom date range inputs
    const startDateInput = page.locator('[data-testid="start-date-input"]')
    const endDateInput = page.locator('[data-testid="end-date-input"]')
    
    // Test invalid date range (end date before start date)
    await startDateInput.fill('2023-12-15')
    await endDateInput.fill('2023-12-10') // Earlier than start date
    
    // Verify validation error message
    await expect(page.getByText('終了日は開始日より後の日付を選択してください')).toBeVisible()
    
    // Verify search is not triggered with invalid range
    await expect(page.getByText('検索中...')).not.toBeVisible()
  })

  test('should handle invalid search parameters gracefully', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock API returning validation errors
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Invalid search parameters',
          details: { date_range: 'Invalid date format' }
        })
      })
    })
    
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [{ name: 'TestTag', count: 1 }]
        })
      })
    })
    
    // Trigger search
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=TestTag')
    
    // Verify API validation error is handled
    await page.waitForSelector('text=エラーが発生しました', { timeout: 10000 })
    await expect(page.getByText('Invalid search parameters')).toBeVisible()
  })

  test('should handle unauthorized access gracefully', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock unauthorized response
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Unauthorized' })
      })
    })
    
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [{ name: 'TestTag', count: 1 }]
        })
      })
    })
    
    // Trigger search
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=TestTag')
    
    // Verify unauthorized error handling
    await page.waitForSelector('text=エラーが発生しました', { timeout: 10000 })
    await expect(page.getByText('認証が必要です')).toBeVisible()
  })

  test('should handle rate limiting errors', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock rate limit response
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 429,
        contentType: 'application/json',
        body: JSON.stringify({ 
          error: 'Rate limit exceeded',
          retry_after: 60
        })
      })
    })
    
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [{ name: 'TestTag', count: 1 }]
        })
      })
    })
    
    // Trigger search
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=TestTag')
    
    // Verify rate limit error handling
    await page.waitForSelector('text=エラーが発生しました', { timeout: 10000 })
    await expect(page.getByText('リクエストが多すぎます')).toBeVisible()
  })

  test('should handle empty/corrupted filter data', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock corrupted tags response
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: null // Corrupted data
        })
      })
    })
    
    await page.route('**/api/v1/search/authors', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          authors: [] // Empty authors list
        })
      })
    })
    
    // Wait for page to load and handle corrupted data
    await page.waitForTimeout(2000)
    
    // Verify graceful handling of corrupted/empty data
    await expect(page.getByText('タグの読み込みに失敗しました')).toBeVisible()
    await expect(page.getByText('利用可能な作成者がありません')).toBeVisible()
    
    // Verify search functionality is not completely broken
    await expect(page.getByRole('heading', { name: '検索フィルター' })).toBeVisible()
  })

  test('should handle browser offline state', async ({ page, context }) => {
    await page.goto('/app/search')
    
    // Set browser to offline mode
    await context.setOffline(true)
    
    // Try to trigger search
    await page.click('text=過去7日間')
    
    // Verify offline error handling
    await page.waitForSelector('text=エラーが発生しました', { timeout: 10000 })
    await expect(page.getByText('ネットワークエラー')).toBeVisible()
    
    // Restore online mode
    await context.setOffline(false)
    
    // Verify retry works after coming back online
    await page.click('button:has-text("再試行")')
    await expect(page.getByText('検索中...')).toBeVisible()
  })

  test('should handle malformed API responses', async ({ page }) => {
    await page.goto('/app/search')
    
    // Mock malformed JSON response
    await page.route('**/api/v1/search/whiteboards', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: 'invalid json response'
      })
    })
    
    await page.route('**/api/v1/search/tags', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tags: [{ name: 'TestTag', count: 1 }]
        })
      })
    })
    
    // Trigger search
    await page.waitForSelector('[data-testid="tag-filter"]')
    await page.click('[data-testid="tag-filter"] .multiselect')
    await page.click('text=TestTag')
    
    // Verify malformed response handling
    await page.waitForSelector('text=エラーが発生しました', { timeout: 10000 })
    await expect(page.getByText('データの解析に失敗しました')).toBeVisible()
  })
})