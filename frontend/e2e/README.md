# 検索機能のE2Eテスト

このディレクトリには、ホワイトボードアプリケーションの高度な検索機能のEnd-to-End (E2E) テストが含まれています。Issue #21のタスク8.3の要件を実装したものです。

## 📚 E2Eテストとは？

E2E（End-to-End）テストは、実際のユーザーがブラウザでアプリケーションを操作するのと同じように、自動化されたテストを実行する手法です。ユニットテストや統合テストでは発見できない、実際の使用環境での問題を検出できます。

## 📁 テストファイル構成

```
e2e/
├── search-workflow.spec.ts         # 主要な検索ワークフローテスト
├── search-components.spec.ts       # 個別コンポーネントの動作テスト
├── search-error-scenarios.spec.ts  # エラーハンドリングとエッジケーステスト
├── search-performance.spec.ts      # パフォーマンスとREQ-6要件準拠テスト
├── search-main-scenarios.spec.ts   # Issue #21 8.3 主要シナリオテスト（新規実装）
└── README.md                      # このドキュメント
```

### 各ファイルの役割詳細

- **search-workflow.spec.ts**: ユーザーが実際に行う検索の流れをテスト
- **search-components.spec.ts**: フィルターなど個別部品の詳細な動作をチェック  
- **search-error-scenarios.spec.ts**: ネットワークエラーなど異常時の動作を確認
- **search-performance.spec.ts**: 速度要件（200ms以内）への準拠を検証
- **search-main-scenarios.spec.ts**: Issue #21 Section 8.3で要求される主要シナリオテストを包括的に実装

## 🧪 Test Coverage

### Main Search Workflow (`search-workflow.spec.ts`)
- **Navigation & Initial State**: Page routing, SEO meta tags, initial empty state
- **Filter Interactions**: Tag, author, and date range filter functionality
- **Multi-filter Search**: Complex search scenarios with multiple active filters
- **Sort Functionality**: Result sorting by different criteria
- **Error & Empty States**: Graceful handling of no results and errors
- **Mobile Responsiveness**: Responsive design verification

### Component Tests (`search-components.spec.ts`)
- **TagFilter**: Multiselect interactions, tag selection/deselection
- **AuthorFilter**: Author selection, "自分のホワイトボード" quick filter
- **DateRangeFilter**: Preset buttons, custom date range, validation
- **ActiveFilters**: Filter display, individual and bulk removal
- **SearchResults**: Result cards, metadata display, pagination
- **Accessibility**: Keyboard navigation, ARIA labels, screen reader support

### Error Scenarios (`search-error-scenarios.spec.ts`)
- **Network Errors**: API failures, timeouts, offline handling
- **Validation Errors**: Invalid date ranges, malformed parameters
- **Authentication**: Unauthorized access, session expiration
- **Rate Limiting**: 429 responses, retry logic
- **Data Corruption**: Malformed API responses, empty datasets

### Performance Tests (`search-performance.spec.ts`)
- **Response Time**: REQ-6 compliance (< 200ms search API response)
- **UI Responsiveness**: Maintaining interactivity during searches
- **Large Datasets**: Handling 1000+ results efficiently
- **Debouncing**: Preventing excessive API calls during rapid filter changes
- **Page Load Performance**: Initial page load optimization
- **Concurrent Searches**: Race condition handling

### Main Scenario Tests (`search-main-scenarios.spec.ts`) - Issue #21 8.3 Implementation
- **Main Scenario 1**: Tag-based Search with AND Logic - @vueform/multiselect タグ選択とAND検索動作の完全テスト
- **Main Scenario 2**: Author Search with Quick Filter - 作成者選択、OR検索、「自分のホワイトボード」クイックフィルターの検証
- **Main Scenario 3**: Date Range Search with Presets and Validation - Vue Tailwind Datepicker、プリセット機能、バリデーションの包括テスト
- **Main Scenario 4**: Complex Multi-filter Search with Real-time Updates - マルチフィルター組み合わせとリアルタイム結果更新の確認
- **Main Scenario 5**: Search Results Operations and Navigation - ページネーション、ソート、ホワイトボード詳細遷移の動作検証
- **Main Scenario 6**: Error Scenarios and User Experience - ネットワークエラー、バリデーション、フォールバック動作の確認

## 🚀 Running Tests

### Prerequisites

Make sure you have the development environment set up:

```bash
# Install dependencies
npm install

# Ensure Playwright browsers are installed
npx playwright install
```

### Test Commands

```bash
# Run all E2E tests
npm run test:e2e

# Run tests in headed mode (see browser)
npx playwright test --headed

# Run specific test file
npx playwright test search-workflow

# Run tests in specific browser
npx playwright test --project=chromium

# Run tests in debug mode
npx playwright test --debug

# Generate test report
npx playwright test --reporter=html
```

### Docker Environment

As specified in Issue #21, **Docker environment execution is mandatory**:

```bash
# Start the complete environment
docker-compose up -d

# Install Playwright browsers and dependencies (first time setup)
docker-compose exec frontend npx playwright install chromium
docker-compose exec frontend npx playwright install-deps  # May require root access

# Run E2E tests in Docker with proper environment variables
docker-compose exec frontend bash -c "DOCKER=true npm run test:e2e"

# Run specific main scenario tests
docker-compose exec frontend bash -c "DOCKER=true npx playwright test search-main-scenarios --project chromium"

# View test results
docker-compose exec frontend npx playwright show-report
```

**Note**: Docker環境でのPlaywright実行には追加の設定が必要です：
- `DOCKER=true` 環境変数により、baseURLが3000番ポートに設定されます
- システム依存関係のインストールにはroot権限が必要な場合があります
- Chromiumブラウザのダウンロードとインストールが初回実行時に必要です

## 🎯 Test Scenarios

### Main User Journeys

1. **Search Page Navigation**
   ```typescript
   // Navigate to search page and verify initial state
   await page.goto('/app/search')
   await expect(page.getByRole('heading', { name: 'ホワイトボード検索' })).toBeVisible()
   ```

2. **Tag-based Search**
   ```typescript
   // Select tags and verify results
   await page.click('[data-testid="tag-filter"] .multiselect')
   await page.click('text=Vue.js')
   await expect(page.getByText('タグ: Vue.js')).toBeVisible()
   ```

3. **Multi-filter Complex Search**
   ```typescript
   // Apply multiple filters simultaneously
   await page.click('text=Vue.js')           // Tag filter
   await page.click('text=自分のホワイトボード') // Author filter
   await page.click('text=過去7日間')         // Date filter
   ```

4. **Performance Validation**
   ```typescript
   // Verify REQ-6 compliance (< 200ms response)
   const startTime = Date.now()
   await page.click('[data-testid="tag-filter"] .multiselect')
   await page.waitForSelector('[data-testid="search-results"]')
   const responseTime = Date.now() - startTime
   expect(responseTime).toBeLessThan(200)
   ```

## 🔧 Configuration

### Playwright Configuration (`../playwright.config.ts`)

- **Base URL**: `http://localhost:5173` (Vite dev server)
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari
- **Retry Policy**: 2 retries in CI, 0 in local development
- **Artifacts**: Screenshots on failure, traces on retry
- **Dev Server**: Auto-starts Vite dev server before tests

### Test Data Management

Tests use **API mocking** for consistent, isolated testing:

```typescript
// Mock search API responses
await page.route('**/api/v1/search/whiteboards', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      whiteboards: [...],
      total: 100
    })
  })
})
```

## 📊 Metrics & Reports

### Coverage Metrics
- **Functional Coverage**: All REQ-1 through REQ-6 requirements
- **Browser Coverage**: 5 browser/device combinations
- **Error Coverage**: Network, validation, authentication, rate limiting
- **Performance Coverage**: Response time, UI responsiveness, large datasets

### Test Reports
- **HTML Report**: `npx playwright show-report`
- **JUnit XML**: `test-results/junit.xml`
- **Screenshots**: Captured on test failures
- **Video**: Recorded for failed tests

## 🐛 Debugging

### Local Debugging
```bash
# Run with browser visible
npx playwright test --headed

# Debug specific test
npx playwright test search-workflow --debug

# Generate trace files
npx playwright test --trace on
```

### Common Issues

1. **Element Not Found**: Verify `data-testid` attributes are present
2. **Timing Issues**: Use `page.waitForSelector()` for dynamic content
3. **API Mocking**: Ensure route mocking is set up before navigation
4. **Authentication**: Check that auth state is properly mocked in `beforeEach`

## 🔗 Related Requirements

This E2E test suite directly addresses **Issue #21, Section 8.3**:

- ✅ **Playwright設定**: Complete configuration with multi-browser support and Docker environment compatibility
- ✅ **検索ページナビゲーション**: `/search` route testing and rendering
- ✅ **Vue Router統合**: SPA routing and navigation verification  
- ✅ **SEO対応**: Meta tags and page title validation
- ✅ **主要シナリオテスト**: 6つの包括的なメインシナリオテスト実装完了 (`search-main-scenarios.spec.ts`)
  - タグ検索 (AND logic with @vueform/multiselect)
  - 作成者検索 (OR logic + クイックフィルター)
  - 日付範囲検索 (Vue Tailwind Datepicker + プリセット + バリデーション)
  - 複合検索 (マルチフィルター + リアルタイム更新)
  - 検索結果操作 (ページネーション + ソート + 詳細遷移)
  - エラーシナリオ (ネットワークエラー + バリデーション + UX)
- ✅ **エラーシナリオテスト**: Network errors, validation, fallback behaviors
- ✅ **パフォーマンステスト**: REQ-6 compliance (< 200ms response time)

## 📝 Maintenance

### Adding New Tests
1. Create test files in the `e2e/` directory
2. Follow the existing naming convention: `feature-aspect.spec.ts`
3. Use `data-testid` attributes for reliable element selection
4. Include API mocking for isolated testing
5. Add appropriate assertions for both success and error cases

### Updating Tests
- Keep tests in sync with component changes
- Update API mocks when backend interfaces change
- Adjust performance thresholds based on actual requirements
- Maintain browser compatibility across all supported platforms