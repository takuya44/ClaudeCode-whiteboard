import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import type { User, AuthState } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = async (email: string, password: string) => {
    isLoading.value = true
    try {
      // TODO: API call to login endpoint
      // const response = await api.post('/auth/login', { email, password })
      // user.value = response.data.user
      // token.value = response.data.token
      // localStorage.setItem('auth_token', token.value)
      
      console.log('Login attempt:', { email, password })
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

  const register = async (userData: Omit<User, 'id' | 'createdAt' | 'updatedAt'>) => {
    isLoading.value = true
    try {
      // TODO: API call to register endpoint
      // const response = await api.post('/auth/register', userData)
      // user.value = response.data.user
      // token.value = response.data.token
      // localStorage.setItem('auth_token', token.value)
      
      console.log('Register attempt:', userData)
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
      // TODO: API call to verify token and get user data
      // const response = await api.get('/auth/me')
      // user.value = response.data
      
      console.log('Checking auth with token:', storedToken)
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