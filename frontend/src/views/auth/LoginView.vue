<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Sign in to your account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Or
          <router-link
            to="/register"
            class="font-medium text-primary-600 hover:text-primary-500"
          >
            create a new account
          </router-link>
        </p>
      </div>
      
      <form
        class="mt-8 space-y-6"
        @submit.prevent="handleSubmit"
      >
        <div class="space-y-4">
          <BaseInput
            v-model="form.email"
            type="email"
            label="Email address"
            placeholder="Enter your email"
            required
            :error="errors.email"
          />
          
          <BaseInput
            v-model="form.password"
            type="password"
            label="Password"
            placeholder="Enter your password"
            required
            :error="errors.password"
          />
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.rememberMe"
              name="remember-me"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            >
            <label
              for="remember-me"
              class="ml-2 block text-sm text-gray-900"
            >
              Remember me
            </label>
          </div>

          <div class="text-sm">
            <a
              href="#"
              class="font-medium text-primary-600 hover:text-primary-500"
            >
              Forgot your password?
            </a>
          </div>
        </div>

        <BaseButton
          type="submit"
          block
          :loading="isLoading"
          loading-text="Signing in..."
        >
          Sign in
        </BaseButton>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { BaseInput, BaseButton } from '@/components/ui'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  password: '',
  rememberMe: false
})

const errors = ref<Record<string, string>>({})
const isLoading = ref(false)

const validateForm = () => {
  errors.value = {}
  
  if (!form.email) {
    errors.value.email = 'Email is required'
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.value.email = 'Email is invalid'
  }
  
  if (!form.password) {
    errors.value.password = 'Password is required'
  } else if (form.password.length < 6) {
    errors.value.password = 'Password must be at least 6 characters'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isLoading.value = true
  
  try {
    await authStore.login(form.email, form.password)
    
    // Redirect to intended page or dashboard
    const redirect = router.currentRoute.value.query.redirect as string
    router.push(redirect || '/dashboard')
  } catch (error) {
    console.error('Login failed:', error)
    errors.value.general = 'Invalid email or password'
  } finally {
    isLoading.value = false
  }
}
</script>