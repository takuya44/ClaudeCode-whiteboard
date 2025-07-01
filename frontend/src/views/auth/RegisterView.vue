<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          アカウントを作成
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          または
          <router-link
            to="/login"
            class="font-medium text-primary-600 hover:text-primary-500"
          >
            既存のアカウントでログイン
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
            label="お名前"
            placeholder="お名前を入力"
            required
            :error="errors.name"
          />
          
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
          
          <BaseInput
            v-model="form.confirmPassword"
            type="password"
            label="パスワード確認"
            placeholder="パスワードを再入力"
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

            <a
              href="#"
              class="text-primary-600 hover:text-primary-500"
            >利用規約</a>
            および
            <a
              href="#"
              class="text-primary-600 hover:text-primary-500"
            >プライバシーポリシー</a>
            に同意します
          </label>
        </div>

        <BaseButton
          type="submit"
          block
          :loading="isLoading"
          loading-text="アカウント作成中..."
        >
          アカウント作成
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
    errors.value.name = 'お名前が必要です'
  }
  
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
  
  if (!form.confirmPassword) {
    errors.value.confirmPassword = 'パスワードを確認してください'
  } else if (form.password !== form.confirmPassword) {
    errors.value.confirmPassword = 'パスワードが一致しません'
  }
  
  if (!form.agreeToTerms) {
    errors.value.agreeToTerms = '利用規約に同意する必要があります'
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
    errors.value.general = '登録に失敗しました。もう一度お試しください。'
  } finally {
    isLoading.value = false
  }
}
</script>