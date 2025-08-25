<template>
  <div class="search-results" data-testid="search-results">
    <!-- Results Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      <ResultCard
        v-for="whiteboard in searchStore.searchResults"
        :key="whiteboard.id"
        :whiteboard="whiteboard"
      />
    </div>

    <!-- Pagination -->
    <div
      v-if="searchStore.totalResults > searchStore.pageSize"
      class="border-t border-gray-200 bg-white px-6 py-4"
    >
      <div class="flex items-center justify-between">
        <!-- Results Info -->
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            v-if="searchStore.currentPage > 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            @click="goToPreviousPage"
          >
            前へ
          </button>
          <button
            v-if="searchStore.hasNextPage"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            @click="goToNextPage"
          >
            次へ
          </button>
        </div>

        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <!-- Results Count -->
          <div>
            <p class="text-sm text-gray-700">
              <span class="font-medium">{{ startResult }}</span>
              から
              <span class="font-medium">{{ endResult }}</span>
              まで（全
              <span class="font-medium">{{ searchStore.totalResults }}</span>
              件）
            </p>
          </div>

          <!-- Pagination Controls -->
          <div>
            <nav
              class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
              aria-label="Pagination"
            >
              <!-- Previous Page -->
              <button
                :disabled="searchStore.currentPage <= 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                @click="goToPreviousPage"
              >
                <span class="sr-only">前のページ</span>
                <svg
                  class="h-5 w-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                >
                  <path
                    fill-rule="evenodd"
                    d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>

              <!-- Page Numbers -->
              <template
                v-for="page in visiblePages"
                :key="page"
              >
                <button
                  v-if="page === '...'"
                  class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
                  disabled
                >
                  ...
                </button>
                <button
                  v-else
                  :class="[
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                    page === searchStore.currentPage
                      ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                  ]"
                  @click="goToPage(page as number)"
                >
                  {{ page }}
                </button>
              </template>

              <!-- Next Page -->
              <button
                :disabled="!searchStore.hasNextPage"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                @click="goToNextPage"
              >
                <span class="sr-only">次のページ</span>
                <svg
                  class="h-5 w-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                >
                  <path
                    fill-rule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>

      <!-- Page Size Selector -->
      <div class="mt-4 flex items-center justify-center sm:justify-start">
        <div class="flex items-center space-x-2">
          <label
            for="page-size-select"
            class="text-sm text-gray-700"
          >1ページあたりの表示件数:</label>
          <select
            id="page-size-select"
            :value="searchStore.pageSize"
            class="border border-gray-300 rounded-md text-sm focus:ring-indigo-500 focus:border-indigo-500"
            @change="handlePageSizeChange"
          >
            <option value="10">
              10件
            </option>
            <option value="20">
              20件
            </option>
            <option value="50">
              50件
            </option>
            <option value="100">
              100件
            </option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSearchStore } from '@/stores/search'
import ResultCard from './ResultCard.vue'

const searchStore = useSearchStore()

// Pagination computed properties
const startResult = computed(() => {
  return (searchStore.currentPage - 1) * searchStore.pageSize + 1
})

const endResult = computed(() => {
  const end = searchStore.currentPage * searchStore.pageSize
  return Math.min(end, searchStore.totalResults)
})

// Visible page numbers (with ellipsis)
const visiblePages = computed(() => {
  const current = searchStore.currentPage
  const total = searchStore.totalPages
  const pages: (number | string)[] = []

  if (total <= 7) {
    // Show all pages if total is 7 or less
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Always show first page
    pages.push(1)

    if (current > 4) {
      pages.push('...')
    }

    // Show pages around current page
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)

    for (let i = start; i <= end; i++) {
      if (!pages.includes(i)) {
        pages.push(i)
      }
    }

    if (current < total - 3) {
      pages.push('...')
    }

    // Always show last page
    if (!pages.includes(total)) {
      pages.push(total)
    }
  }

  return pages
})

// Navigation methods
const goToPage = (page: number) => {
  if (page !== searchStore.currentPage && page >= 1 && page <= searchStore.totalPages) {
    searchStore.setCurrentPage(page)
  }
}

const goToPreviousPage = () => {
  if (searchStore.currentPage > 1) {
    searchStore.setCurrentPage(searchStore.currentPage - 1)
  }
}

const goToNextPage = () => {
  if (searchStore.hasNextPage) {
    searchStore.setCurrentPage(searchStore.currentPage + 1)
  }
}

const handlePageSizeChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const newPageSize = parseInt(target.value, 10)
  searchStore.setPageSize(newPageSize)
}
</script>