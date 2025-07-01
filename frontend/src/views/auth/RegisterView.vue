<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Or
          <router-link
            to="/login"
            class="font-medium text-primary-600 hover:text-primary-500"
          >
            sign in to your existing account
          </router-link>
        </p>
      </div>
      
      <form
        class="mt-8 space-y-6"
        @submit.prevent="handleSubmit"
      >
        <div class="space-y-4">
          <BaseInput
            v-model="form.name"
            label="Full Name"
            placeholder="Enter your full name"
            required
            :error="errors.name"
          />
          
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
          
          <BaseInput
            v-model="form.confirmPassword"
            type="password"
            label="Confirm Password"
            placeholder="Confirm your password"
            required
            :error="errors.confirmPassword"
          />
        </div>

        <div class="flex items-center">
          <input
            id="agree-terms"
            v-model="form.agreeToTerms"
            name="agree-terms"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          >
          <label
            for="agree-terms"
            class="ml-2 block text-sm text-gray-900"
          >
            I agree to the 
            <a
              href="#"
              class="text-primary-600 hover:text-primary-500"
            >Terms of Service</a>
            and 
            <a
              href="#"
              class="text-primary-600 hover:text-primary-500"
            >Privacy Policy</a>
          </label>
        </div>

        <BaseButton
          type="submit"
          block
          :loading="isLoading"
          loading-text="Creating account..."
        >
          Create Account
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
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false
})

const errors = ref<Record<string, string>>({})
const isLoading = ref(false)

const validateForm = () => {
  errors.value = {}
  
  if (!form.name.trim()) {
    errors.value.name = 'Name is required'
  }
  
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
  
  if (!form.confirmPassword) {
    errors.value.confirmPassword = 'Please confirm your password'
  } else if (form.password !== form.confirmPassword) {
    errors.value.confirmPassword = 'Passwords do not match'
  }
  
  if (!form.agreeToTerms) {
    errors.value.agreeToTerms = 'You must agree to the terms of service'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isLoading.value = true
  
  try {
    await authStore.register({
      name: form.name,
      email: form.email,
      role: 'user'
    })
    
    router.push('/dashboard')
  } catch (error) {
    console.error('Registration failed:', error)
    errors.value.general = 'Registration failed. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>