export interface Tag {
  id: string
  name: string
  color?: string
  usageCount?: number
}

export interface DateRange {
  start: Date | null
  end: Date | null
  type: 'created' | 'updated'
}

export interface SearchFilters {
  tags: string[]
  authors: string[]
  dateRange: DateRange | null  // dateRangeはnullを許可（未設定時のため）
  sortBy: 'created_at' | 'updated_at' | 'title'
  sortOrder: 'asc' | 'desc'
}

export interface WhiteboardSearchResult {
  id: string
  title: string
  description: string
  creator: {
    id: string
    name: string
    avatar?: string
  }
  tags: Tag[]
  createdAt: Date
  updatedAt: Date
  isPublic: boolean
  collaboratorCount: number
}

export interface SearchResponse {
  results: WhiteboardSearchResult[]
  total: number
  page: number
  pageSize: number
  hasNext: boolean
}

export interface PaginationParams {
  page: number
  pageSize: number
}

export interface ValidationResult {
  isValid: boolean
  errors: Record<string, string[]>
}

export interface DatePreset {
  label: string
  value: () => DateRange
}