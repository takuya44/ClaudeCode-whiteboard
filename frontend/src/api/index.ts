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

export const apiRequest = {
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await api.get(url, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message || 'Request failed',
        errors: error.response?.data?.errors
      }
    }
  },
  
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await api.post(url, data, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message || 'Request failed',
        errors: error.response?.data?.errors
      }
    }
  },
  
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await api.put(url, data, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message || 'Request failed',
        errors: error.response?.data?.errors
      }
    }
  },
  
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await api.patch(url, data, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message || 'Request failed',
        errors: error.response?.data?.errors
      }
    }
  },
  
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await api.delete(url, config)
      return { 
        success: true, 
        data: response.data 
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message || 'Request failed',
        errors: error.response?.data?.errors
      }
    }
  },
}

export default api