import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SearchFilters, WhiteboardSearchResult, SearchResponse } from '@/types/search'

export const useSearchStore = defineStore('search', () => {
  // State
  const filters = ref<SearchFilters>({
    tags: [],
    authors: [],
    dateRange: {
      start: null,
      end: null,
      type: 'created'
    },
    sortBy: 'updated_at',
    sortOrder: 'desc'
  })

  const searchResults = ref<WhiteboardSearchResult[]>([])
  const totalResults = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasActiveFilters = computed(() => {
    return filters.value.tags.length > 0 ||
           filters.value.authors.length > 0 ||
           filters.value.dateRange.start !== null ||
           filters.value.dateRange.end !== null
  })

  const hasNextPage = computed(() => {
    return currentPage.value * pageSize.value < totalResults.value
  })

  const totalPages = computed(() => {
    return Math.ceil(totalResults.value / pageSize.value)
  })

  // Actions
  const updateFilters = (newFilters: Partial<SearchFilters>) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const clearFilters = () => {
    filters.value = {
      tags: [],
      authors: [],
      dateRange: {
        start: null,
        end: null,
        type: 'created'
      },
      sortBy: 'updated_at',
      sortOrder: 'desc'
    }
    currentPage.value = 1
  }

  const setSearchResults = (response: SearchResponse) => {
    searchResults.value = response.results
    totalResults.value = response.total
    error.value = null
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const setCurrentPage = (page: number) => {
    currentPage.value = page
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1 // Reset to first page when changing page size
  }

  return {
    // State
    filters,
    searchResults,
    totalResults,
    currentPage,
    pageSize,
    isLoading,
    error,
    // Computed
    hasActiveFilters,
    hasNextPage,
    totalPages,
    // Actions
    updateFilters,
    clearFilters,
    setSearchResults,
    setLoading,
    setError,
    setCurrentPage,
    setPageSize
  }
})