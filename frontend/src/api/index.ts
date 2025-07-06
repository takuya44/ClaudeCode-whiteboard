import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types'

const baseURL = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api/v1` : 'http://localhost:8000/api/v1'

const api: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

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

api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

// Helper function to format error messages consistently
const formatErrorMessage = (error: any, method: string, url?: string): string => {
  const prefix = url ? `${method} ${url}` : method
  
  if (error.response) {
    // Server responded with error status
    const status = error.response.status
    const detail = error.response.data?.detail || error.response.data?.message || 'Unknown server error'
    return `${prefix} failed (${status}): ${detail}`
  } else if (error.request) {
    // Request was made but no response received
    return `${prefix} failed: No response from server`
  } else {
    // Something else happened
    return `${prefix} failed: ${error.message || 'Unknown error'}`
  }
}

// Helper function to log request details for debugging
const logRequest = (method: string, url: string, data?: any) => {
  if (import.meta.env.DEV) {
    console.log(`API ${method} ${url}`, data ? { data } : '')
  }
}

export const apiRequest = {
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      logRequest('GET', url)
      const response = await api.get(url, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      console.error('API GET error:', error)
      return {
        success: false,
        message: formatErrorMessage(error, 'GET', url),
        data: null as T
      }
    }
  },
  
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      logRequest('POST', url, data)
      const response = await api.post(url, data, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      console.error('API POST error:', error)
      return {
        success: false,
        message: formatErrorMessage(error, 'POST', url),
        data: null as T
      }
    }
  },
  
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      logRequest('PUT', url, data)
      const response = await api.put(url, data, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      console.error('API PUT error:', error)
      return {
        success: false,
        message: formatErrorMessage(error, 'PUT', url),
        data: null as T
      }
    }
  },
  
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      logRequest('PATCH', url, data)
      const response = await api.patch(url, data, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      console.error('API PATCH error:', error)
      return {
        success: false,
        message: formatErrorMessage(error, 'PATCH', url),
        data: null as T
      }
    }
  },
  
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      logRequest('DELETE', url)
      const response = await api.delete(url, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      console.error('API DELETE error:', error)
      return {
        success: false,
        message: formatErrorMessage(error, 'DELETE', url),
        data: null as T
      }
    }
  },
}

export default api