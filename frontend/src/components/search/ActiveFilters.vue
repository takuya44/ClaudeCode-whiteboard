<template>
  <div class="active-filters mb-6">
    <h3 class="text-sm font-medium text-gray-700 mb-3">
      アクティブなフィルター
    </h3>
    
    <div class="space-y-3">
      <!-- Active Tags -->
      <div
        v-if="activeTags.length > 0"
        class="filter-group"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-medium text-gray-600">タグ</span>
          <button
            type="button"
            class="text-xs text-red-500 hover:text-red-700"
            @click="clearTags"
          >
            すべてクリア
          </button>
        </div>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="tag in activeTags"
            :key="tag.id"
            class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
          >
            <div
              v-if="tag.color"
              class="w-2 h-2 rounded-full mr-1.5 flex-shrink-0"
              :style="{ backgroundColor: tag.color }"
            />
            {{ tag.name }}
            <button
              type="button"
              class="ml-1 text-indigo-400 hover:text-indigo-600"
              :aria-label="`タグ「${tag.name}」を削除`"
              @click="removeTag(tag.id)"
            >
              <svg
                class="w-3 h-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </span>
        </div>
      </div>


      <!-- Active Authors -->
      <div
        v-if="searchStore.filters.authors.length > 0"
        class="filter-group"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-medium text-gray-600">作成者</span>
          <button
            type="button"
            class="text-xs text-red-500 hover:text-red-700"
            @click="clearAuthors"
          >
            すべてクリア
          </button>
        </div>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="authorId in searchStore.filters.authors"
            :key="authorId"
            class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
          >
            <!-- Small Avatar -->
            <div class="w-3 h-3 rounded-full mr-1.5 flex-shrink-0">
              <img
                v-if="getAuthorById(authorId)?.avatar"
                :src="getAuthorById(authorId)?.avatar"
                :alt="getAuthorById(authorId)?.name"
                class="w-full h-full rounded-full object-cover"
              >
              <div
                v-else
                class="w-full h-full rounded-full bg-blue-300 flex items-center justify-center"
              >
                <span class="text-xs font-medium text-blue-700 uppercase leading-none">
                  {{ getInitials(getAuthorById(authorId)?.name || authorId) }}
                </span>
              </div>
            </div>
            {{ getAuthorById(authorId)?.name || `作成者ID: ${authorId}` }}
            <button
              type="button"
              class="ml-1 text-blue-400 hover:text-blue-600"
              :aria-label="`作成者「${getAuthorById(authorId)?.name || authorId}」を削除`"
              @click="removeAuthor(authorId)"
            >
              <svg
                class="w-3 h-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </span>
        </div>
      </div>

      <!-- Active Date Range -->
      <div
        v-if="hasActiveDateRange"
        class="filter-group"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-medium text-gray-600">
            {{ dateRange?.type === 'created' ? '作成日' : '更新日' }}
          </span>
          <button
            type="button"
            class="text-xs text-red-500 hover:text-red-700"
            @click="clearDateRange"
          >
            クリア
          </button>
        </div>
        <div class="flex items-center space-x-2 text-xs">
          <span class="inline-flex items-center px-2 py-1 rounded-full bg-green-100 text-green-800 font-medium">
            <svg
              class="w-3 h-3 mr-1"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M9 11H7v6h2v-6zm4 0h-2v6h2v-6zm4 0h-2v6h2v-6zm2-7h-3V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H5V9h14v11z" />
            </svg>
            {{ formatDateRangeDisplay() }}
          </span>
        </div>
      </div>

      <!-- Sort Option Display -->
      <div
        v-if="!isDefaultSort"
        class="filter-group"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-medium text-gray-600">並び替え</span>
          <button
            type="button"
            class="text-xs text-red-500 hover:text-red-700"
            @click="resetSort"
          >
            リセット
          </button>
        </div>
        <div class="text-xs">
          <span class="inline-flex items-center px-2 py-1 rounded-full bg-purple-100 text-purple-800 font-medium">
            <svg
              class="w-3 h-3 mr-1"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z" />
            </svg>
            {{ getSortDisplayText() }}
          </span>
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div class="mt-3 pt-3 border-t border-gray-200">
      <div class="text-xs text-gray-500 text-center">
        {{ getFilterSummary() }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSearchStore } from '@/stores/search'

const searchStore = useSearchStore()

// Get active filter data
const activeTags = computed(() => {
  return (searchStore.availableTags || []).filter(tag => 
    searchStore.filters.tags.includes(tag.id)
  )
})

const activeAuthors = computed(() => {
  return (searchStore.availableAuthors || []).filter(author => 
    searchStore.filters.authors.includes(author.id)
  )
})

const dateRange = computed(() => searchStore.filters.dateRange)

const hasActiveDateRange = computed(() => {
  return dateRange.value && (dateRange.value.start !== null || dateRange.value.end !== null)
})

const isDefaultSort = computed(() => {
  return searchStore.filters.sortBy === 'updated_at' && searchStore.filters.sortOrder === 'desc'
})

// Filter management actions
const removeTag = (tagId: string) => {
  const newTags = searchStore.filters.tags.filter(id => id !== tagId)
  searchStore.updateFilters({ tags: newTags })
  // watcherが自動的に検索を実行するため、手動実行は不要
}

const removeAuthor = (authorId: string) => {
  const newAuthors = searchStore.filters.authors.filter(id => id !== authorId)
  searchStore.updateFilters({ authors: newAuthors })
  // watcherが自動的に検索を実行するため、手動実行は不要
}

const clearTags = () => {
  searchStore.updateFilters({ tags: [] })
  // watcherが自動的に検索を実行するため、手動実行は不要
}

const clearAuthors = () => {
  searchStore.updateFilters({ authors: [] })
  // watcherが自動的に検索を実行するため、手動実行は不要
}

const clearDateRange = () => {
  searchStore.updateFilters({
    dateRange: {
      start: null,
      end: null,
      type: dateRange.value?.type || 'created'
    }
  })
  // watcherが自動的に検索を実行するため、手動実行は不要
}

const resetSort = () => {
  searchStore.updateFilters({
    sortBy: 'updated_at',
    sortOrder: 'desc'
  })
}

// Helper functions
const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(part => part.charAt(0))
    .join('')
    .substring(0, 1)
    .toUpperCase()
}

const getAuthorById = (authorId: string) => {
  return searchStore.availableAuthors.find(author => author.id === authorId)
}

const formatDateRangeDisplay = (): string => {
  if (!dateRange.value) return ''
  const start = dateRange.value.start
  const end = dateRange.value.end

  if (start && end) {
    if (isSameDay(start, end)) {
      return formatDate(start)
    }
    return `${formatDate(start)} ～ ${formatDate(end)}`
  }

  if (start) {
    return `${formatDate(start)} 以降`
  }

  if (end) {
    return `${formatDate(end)} 以前`
  }

  return ''
}

const formatDate = (date: Date): string => {
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const isSameDay = (date1: Date, date2: Date): boolean => {
  return date1.toDateString() === date2.toDateString()
}

const getSortDisplayText = (): string => {
  const sortByText = {
    'updated_at': '更新日',
    'created_at': '作成日',
    'title': 'タイトル'
  }[searchStore.filters.sortBy]

  const sortOrderText = searchStore.filters.sortOrder === 'asc' ? '昇順' : '降順'
  
  return `${sortByText}（${sortOrderText}）`
}

const getFilterSummary = (): string => {
  const activeFiltersCount = [
    activeTags.value.length > 0,
    activeAuthors.value.length > 0,
    hasActiveDateRange.value,
    !isDefaultSort.value
  ].filter(Boolean).length

  if (activeFiltersCount === 0) {
    return 'フィルターが設定されていません'
  }

  return `${activeFiltersCount}個のフィルターが適用中`
}
</script>

<style scoped>
.filter-group:not(:last-child) {
  @apply pb-3 border-b border-gray-100;
}
</style>