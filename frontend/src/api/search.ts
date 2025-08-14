import axios from 'axios'
import { toRaw } from 'vue'
import type { SearchFilters, SearchResponse, Tag, DateRange } from '@/types/search'
import type { User } from '@/types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 10000,
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface SearchParams {
  tags: string[]
  authors: string[]
  dateRange?: DateRange | null
  sortBy: 'created_at' | 'updated_at' | 'title'
  sortOrder: 'asc' | 'desc'
  page: number
  pageSize: number
}

class SearchAPI {
  /**
   * ホワイトボード検索を実行
   */
  async searchWhiteboards(params: SearchParams): Promise<SearchResponse> {
    try {
      // Extract pagination params
      const { page, pageSize, ...filters } = params
      
      // Vue.jsのリアクティブオブジェクト(Proxy)をプレーンオブジェクトに変換
      // これによりJSONシリアライズ時の問題を防ぐ（バックエンドで422エラーが発生する原因を解決）
      const requestPayload = {
        tags: toRaw(filters.tags) || [],           // 空配列をデフォルト値とする
        authors: toRaw(filters.authors) || [],     // 空配列をデフォルト値とする
        date_range: filters.dateRange && (filters.dateRange.start || filters.dateRange.end) ? {
          start: filters.dateRange.start?.toISOString(),
          end: filters.dateRange.end?.toISOString(),
          type: filters.dateRange.type
        } : null,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder
      }
      
      // 開発時デバッグ用: 送信するペイロードをログ出力
      console.log('Search API Request Payload:', requestPayload)
      
      const response = await api.post('/search/whiteboards', requestPayload, {
        params: {
          page,
          page_size: pageSize
        }
      })

      // Date strings to Date objects and map backend field names to frontend
      const results = response.data.results.map((result: any) => ({
        id: result.id,
        title: result.title,
        description: result.description,
        creator: result.creator,
        tags: result.tags,
        createdAt: new Date(result.created_at),
        updatedAt: new Date(result.updated_at),
        isPublic: result.is_public,
        collaboratorCount: result.collaborator_count
      }))

      return {
        results,
        total: response.data.total,
        page: response.data.page,
        pageSize: response.data.page_size,
        hasNext: response.data.has_next
      }
    } catch (error: any) {
      console.error('Search API error:', error)
      
      // 422エラー（バリデーションエラー）の場合は詳細なエラーメッセージを提供
      if (error.response?.status === 422) {
        const details = error.response.data?.detail || 'リクエストの形式が正しくありません'
        throw new Error(`検索パラメータエラー: ${details}`)
      }
      
      // その他のエラーは汎用的なメッセージを返す
      throw new Error('検索中にエラーが発生しました')
    }
  }

  /**
   * 利用可能なタグ一覧を取得
   */
  async getAvailableTags(): Promise<Tag[]> {
    try {
      const response = await api.get('/search/tags')
      return response.data
    } catch (error) {
      console.error('Tags API error:', error)
      throw new Error('タグ一覧の取得中にエラーが発生しました')
    }
  }

  /**
   * 作成者一覧を取得
   */
  async getAvailableAuthors(): Promise<User[]> {
    try {
      const response = await api.get('/search/authors')
      return response.data
    } catch (error) {
      console.error('Authors API error:', error)
      throw new Error('作成者一覧の取得中にエラーが発生しました')
    }
  }

  /**
   * 検索フィルターのバリデーション
   */
  async validateFilters(filters: SearchFilters): Promise<{ isValid: boolean; errors: string[] }> {
    try {
      const response = await api.post('/search/validate', filters)
      return response.data
    } catch (error) {
      console.error('Validation API error:', error)
      return { isValid: false, errors: ['フィルターの検証中にエラーが発生しました'] }
    }
  }
}

export const searchAPI = new SearchAPI()