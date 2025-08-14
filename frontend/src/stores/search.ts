import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { SearchFilters, WhiteboardSearchResult, SearchResponse, Tag } from '@/types/search'
import type { User } from '@/types'
import { searchAPI } from '@/api/search'
import { debounce } from '@/utils/debounce'

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

  // Available options
  const availableTags = ref<Tag[]>([])
  const availableAuthors = ref<User[]>([])
  const isLoadingOptions = ref(false)

  // Computed
  const hasActiveFilters = computed(() => {
    return (filters.value.tags?.length ?? 0) > 0 ||
           (filters.value.authors?.length ?? 0) > 0 ||
           (filters.value.dateRange && (filters.value.dateRange.start !== null ||
           filters.value.dateRange.end !== null))
  })

  const hasNextPage = computed(() => {
    return currentPage.value * pageSize.value < totalResults.value
  })

  const totalPages = computed(() => {
    return Math.ceil(totalResults.value / pageSize.value)
  })

  // 型ガード関数
  const isStringArray = (value: any): value is string[] => Array.isArray(value)
  const normalizeToArray = (value: any): string[] => 
    isStringArray(value) ? value : (value ? [value] : [])

  // Actions
  const updateFilters = (newFilters: Partial<SearchFilters>) => {
    // authorsフィールドが文字列で渡される場合があるため、常に配列形式に正規化
    // これはコンポーネント間での型の一貫性を保ち、バックエンドAPI仕様に準拠するため
    if (newFilters.authors !== undefined) {
      newFilters.authors = normalizeToArray(newFilters.authors)
    }
    
    // tagsとauthorsが配列として確実に存在するように保証
    const updatedFilters = { 
      ...filters.value, 
      ...newFilters
    }
    
    // 既存の配列を保持し、undefinedの場合のみ空配列を設定
    if (updatedFilters.tags === undefined) {
      updatedFilters.tags = []
    }
    if (updatedFilters.authors === undefined) {
      updatedFilters.authors = []
    }
    
    // 変更があった場合のみ更新（無限ループ防止）
    const hasChanges = JSON.stringify(filters.value) !== JSON.stringify(updatedFilters)
    if (hasChanges) {
      filters.value = updatedFilters
    }
  }

  const clearFilters = () => {
    // Watcherの無限ループを防ぐため、先に結果をクリア
    searchResults.value = []
    totalResults.value = 0
    currentPage.value = 1
    
    // フィルターを一括更新（Watcherによる検索実行を回避）
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

  // API Actions
  const executeSearch = async () => {
    // アクティブなフィルターがない場合は結果を初期化
    if (!hasActiveFilters.value) {
      searchResults.value = []
      totalResults.value = 0
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await searchAPI.searchWhiteboards({
        ...filters.value,
        page: currentPage.value,
        pageSize: pageSize.value
      })
      setSearchResults(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : '検索中にエラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  const loadAvailableTags = async () => {
    if (availableTags.value.length > 0) return // Already loaded

    isLoadingOptions.value = true
    try {
      availableTags.value = await searchAPI.getAvailableTags()
    } catch (err) {
      console.error('Failed to load tags:', err)
    } finally {
      isLoadingOptions.value = false
    }
  }

  const loadAvailableAuthors = async () => {
    if (availableAuthors.value.length > 0) return // Already loaded

    isLoadingOptions.value = true
    try {
      availableAuthors.value = await searchAPI.getAvailableAuthors()
    } catch (err) {
      console.error('Failed to load authors:', err)
    } finally {
      isLoadingOptions.value = false
    }
  }

  // Debounced search for real-time filtering
  const debouncedSearch = debounce(executeSearch, 300)

  // Safe watcher for filter changes - only triggers when filters have active values
  watch(
    () => ({
      tags: filters.value.tags,
      authors: filters.value.authors,
      dateRange: filters.value.dateRange
    }),
    (newValue, oldValue) => {
      // 初回実行時や完全なクリア時は検索を実行しない
      if (!oldValue) return
      
      // hasActiveFiltersの値を事前計算して無限ループを防ぐ
      const hasActiveTags = (newValue.tags?.length ?? 0) > 0
      const hasActiveAuthors = (newValue.authors?.length ?? 0) > 0
      const hasActiveDateRange = newValue.dateRange && 
        (newValue.dateRange.start !== null || newValue.dateRange.end !== null)
      
      const hasActiveFiltersNow = hasActiveTags || hasActiveAuthors || hasActiveDateRange
      
      // Only trigger search if there are actually active filters
      if (hasActiveFiltersNow) {
        debouncedSearch()
      } else {
        // アクティブフィルターがない場合は結果をクリア
        searchResults.value = []
        totalResults.value = 0
      }
    },
    { deep: true, flush: 'post' }
  )

  return {
    // State
    filters,
    searchResults,
    totalResults,
    currentPage,
    pageSize,
    isLoading,
    error,
    availableTags,
    availableAuthors,
    isLoadingOptions,
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
    setPageSize,
    executeSearch,
    loadAvailableTags,
    loadAvailableAuthors
  }
})