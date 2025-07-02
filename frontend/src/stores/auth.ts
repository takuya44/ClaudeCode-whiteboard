import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import type { User, AuthState } from '@/types'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = async (email: string, password: string) => {
    isLoading.value = true
    try {
      const response = await authApi.login({ email, password })
      
      if (!response.success) {
        throw new Error(response.message || 'Login failed')
      }
      
      // バックエンドから返されるのは access_token なので、それを token として扱う
      token.value = response.data.access_token
      localStorage.setItem('auth_token', token.value)
      
      // ユーザー情報を取得
      await getCurrentUser()
      
      console.log('Login successful:', { email })
    } catch (error) {
      console.error('Login error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
  }

  const getCurrentUser = async () => {
    if (!token.value) return
    
    try {
      const response = await authApi.me()
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to get user info')
      }
      
      user.value = response.data
    } catch (error) {
      console.error('Get current user error:', error)
      logout()
      throw error
    }
  }

  const register = async (userData: { name: string; email: string; password: string }) => {
    isLoading.value = true
    try {
      const response = await authApi.register(userData)
      
      // ユーザー登録後は自動的にユーザー情報が返される
      user.value = response.data
      
      // 登録後は自動ログインをする場合
      // await login(userData.email, userData.password)
      
      console.log('Register successful:', userData)
    } catch (error) {
      console.error('Register error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const checkAuth = async () => {
    const storedToken = localStorage.getItem('auth_token')
    if (!storedToken) return

    token.value = storedToken
    isLoading.value = true
    
    try {
      await getCurrentUser()
      console.log('Auth check successful')
    } catch (error) {
      console.error('Auth check error:', error)
      logout()
    } finally {
      isLoading.value = false
    }
  }

  const updateProfile = async (userData: Partial<User>) => {
    if (!user.value) return

    isLoading.value = true
    try {
      // TODO: API call to update profile
      // const response = await api.put('/auth/profile', userData)
      // user.value = { ...user.value, ...response.data }
      
      user.value = { ...user.value, ...userData }
      console.log('Profile update:', userData)
    } catch (error) {
      console.error('Profile update error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  return {
    user: readonly(user),
    token: readonly(token),
    isLoading: readonly(isLoading),
    isAuthenticated,
    login,
    logout,
    register,
    checkAuth,
    updateProfile,
  }
})