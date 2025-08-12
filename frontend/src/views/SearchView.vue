<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="md:flex md:items-center md:justify-between">
            <div class="flex-1 min-w-0">
              <h1 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                ホワイトボード検索
              </h1>
              <p class="mt-1 text-sm text-gray-500">
                タグ、作成者、日付範囲で絞り込んでホワイトボードを検索
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="lg:grid lg:grid-cols-4 lg:gap-8">
        <!-- Search Filters Sidebar -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
              検索フィルター
            </h2>
            
            <!-- Active Filters Display -->
            <ActiveFilters v-if="searchStore.hasActiveFilters" />
            
            <!-- Tag Filter -->
            <TagFilter class="mb-6" />
            
            <!-- Author Filter -->
            <AuthorFilter class="mb-6" />
            
            <!-- Date Range Filter -->
            <DateRangeFilter />
          </div>
        </div>

        <!-- Search Results -->
        <div class="mt-8 lg:mt-0 lg:col-span-3">
          <!-- Results Header -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-lg font-medium text-gray-900">
                    検索結果
                    <span
                      v-if="searchStore.totalResults > 0"
                      class="text-sm font-normal text-gray-500"
                    >
                      ({{ searchStore.totalResults }}件)
                    </span>
                  </h3>
                </div>
                <div class="flex items-center space-x-4">
                  <!-- Sort Options -->
                  <div class="flex items-center space-x-2">
                    <label
                      for="sort-select"
                      class="text-sm font-medium text-gray-700"
                    >並び替え:</label>
                    <select
                      id="sort-select"
                      :value="`${searchStore.filters.sortBy}_${searchStore.filters.sortOrder}`"
                      class="border border-gray-300 rounded-md text-sm focus:ring-indigo-500 focus:border-indigo-500"
                      @change="handleSortChange"
                    >
                      <option value="updated_at_desc">
                        更新日（新しい順）
                      </option>
                      <option value="updated_at_asc">
                        更新日（古い順）
                      </option>
                      <option value="created_at_desc">
                        作成日（新しい順）
                      </option>
                      <option value="created_at_asc">
                        作成日（古い順）
                      </option>
                      <option value="title_asc">
                        タイトル（昇順）
                      </option>
                      <option value="title_desc">
                        タイトル（降順）
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Loading State -->
            <div
              v-if="searchStore.isLoading"
              class="px-6 py-12 text-center"
            >
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto" />
              <p class="mt-2 text-sm text-gray-500">
                検索中...
              </p>
            </div>

            <!-- Error State -->
            <div
              v-else-if="searchStore.error"
              class="px-6 py-12 text-center"
            >
              <svg
                class="mx-auto h-12 w-12 text-red-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 15c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">
                エラーが発生しました
              </h3>
              <p class="mt-1 text-sm text-gray-500">
                {{ searchStore.error }}
              </p>
              <div class="mt-6">
                <button
                  type="button"
                  class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  @click="searchStore.executeSearch"
                >
                  再試行
                </button>
              </div>
            </div>

            <!-- No Results -->
            <div
              v-else-if="(searchStore.searchResults || []).length === 0 && searchStore.hasActiveFilters"
              class="px-6 py-12 text-center"
            >
              <svg
                class="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">
                ホワイトボードが見つかりませんでした
              </h3>
              <p class="mt-1 text-sm text-gray-500">
                検索条件を変更してもう一度お試しください
              </p>
            </div>

            <!-- Default State (No Filters) -->
            <div
              v-else-if="!searchStore.hasActiveFilters"
              class="px-6 py-12 text-center"
            >
              <svg
                class="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">
                検索フィルターを設定してください
              </h3>
              <p class="mt-1 text-sm text-gray-500">
                左側のフィルターを使用してホワイトボードを検索
              </p>
            </div>

            <!-- Search Results -->
            <SearchResults v-else />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useSearchStore } from '@/stores/search'
import TagFilter from '@/components/search/TagFilter.vue'
import AuthorFilter from '@/components/search/AuthorFilter.vue'
import DateRangeFilter from '@/components/search/DateRangeFilter.vue'
import SearchResults from '@/components/search/SearchResults.vue'
import ActiveFilters from '@/components/search/ActiveFilters.vue'

const searchStore = useSearchStore()

const handleSortChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const value = target.value
  
  // 最後の_で分割して、sortByとsortOrderを正しく取得
  const lastUnderscoreIndex = value.lastIndexOf('_')
  const sortBy = value.substring(0, lastUnderscoreIndex)
  const sortOrder = value.substring(lastUnderscoreIndex + 1)
  
  searchStore.updateFilters({ 
    sortBy: sortBy as 'created_at' | 'updated_at' | 'title',
    sortOrder: sortOrder as 'asc' | 'desc'
  })
}

onMounted(async () => {
  // Load available options for filters
  await Promise.all([
    searchStore.loadAvailableTags(),
    searchStore.loadAvailableAuthors()
  ])
})
</script>