import { apiRequest } from './index'
import type { User, ApiResponse } from '@/types'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  user: User
  access_token: string
}

export interface RegisterRequest {
  name: string
  email: string
  password: string
}

export interface RegisterResponse {
  user: User
  token: string
}

export const authApi = {
  login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    return apiRequest.post('/auth/login', data)
  },

  register(data: RegisterRequest): Promise<ApiResponse<RegisterResponse>> {
    return apiRequest.post('/auth/register', data)
  },

  logout(): Promise<ApiResponse> {
    return apiRequest.post('/auth/logout')
  },

  me(): Promise<ApiResponse<User>> {
    return apiRequest.get('/auth/me')
  },

  updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
    return apiRequest.put('/auth/profile', data)
  },

  changePassword(data: { currentPassword: string; newPassword: string }): Promise<ApiResponse> {
    return apiRequest.post('/auth/change-password', data)
  },

  refreshToken(): Promise<ApiResponse<{ token: string }>> {
    return apiRequest.post('/auth/refresh')
  },
}