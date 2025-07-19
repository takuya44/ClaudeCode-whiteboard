<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          アカウントにログイン
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          または
          <router-link
            to="/register"
            class="font-medium text-primary-600 hover:text-primary-500"
          >
            新規アカウント作成
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
            label="メールアドレス"
            placeholder="メールアドレスを入力"
            required
            :error="errors.email"
          />
          
          <BaseInput
            v-model="form.password"
            type="password"
            label="パスワード"
            placeholder="パスワードを入力"
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
              ログイン状態を保持
            </label>
          </div>

          <div class="text-sm">
            <a
              href="#"
              class="font-medium text-primary-600 hover:text-primary-500"
            >
              パスワードを忘れた場合
            </a>
          </div>
        </div>

        <BaseButton
          type="submit"
          block
          :loading="isLoading"
          loading-text="ログイン中..."
        >
          ログイン
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
    errors.value.email = 'メールアドレスが必要です'
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.value.email = 'メールアドレスが無効です'
  }
  
  if (!form.password) {
    errors.value.password = 'パスワードが必要です'
  } else if (form.password.length < 6) {
    errors.value.password = 'パスワードは6文字以上で入力してください'
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
    router.push(redirect || '/app/dashboard')
  } catch (error) {
    console.error('Login failed:', error)
    errors.value.general = 'メールアドレスまたはパスワードが無効です'
  } finally {
    isLoading.value = false
  }
}
</script>