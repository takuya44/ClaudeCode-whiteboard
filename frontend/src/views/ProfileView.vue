<template>
  <DefaultLayout>
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-3xl mx-auto">
        <div class="bg-white shadow-soft rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h1 class="text-2xl font-bold text-gray-900">
              プロフィール設定
            </h1>
            <p class="text-gray-600">
              アカウント情報と設定を管理します。
            </p>
          </div>
          
          <div class="p-6 space-y-6">
            <form @submit.prevent="handleUpdateProfile">
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
              </div>
              
              <div class="mt-6">
                <BaseButton
                  type="submit"
                  :loading="isLoading"
                  loading-text="更新中..."
                >
                  プロフィール更新
                </BaseButton>
              </div>
            </form>
            
            <hr class="border-gray-200">
            
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">
                パスワード変更
              </h3>
              
              <!-- エラーメッセージ表示 -->
              <div
                v-if="passwordErrors.general"
                class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg"
              >
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg
                      class="h-5 w-5 text-red-400"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <p class="text-sm text-red-600">
                      {{ passwordErrors.general }}
                    </p>
                  </div>
                </div>
              </div>
              
              <!-- 成功メッセージ表示 -->
              <div
                v-if="passwordChangeSuccess"
                class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg"
              >
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg
                      class="h-5 w-5 text-green-400"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <p class="text-sm text-green-600">
                      パスワードが正常に変更されました
                    </p>
                  </div>
                </div>
              </div>
              
              <form @submit.prevent="handleChangePassword">
                <div class="space-y-4">
                  <BaseInput
                    v-model="passwordForm.currentPassword"
                    type="password"
                    label="現在のパスワード"
                    placeholder="現在のパスワードを入力"
                    required
                    :error="passwordErrors.currentPassword"
                  />
                  
                  <BaseInput
                    v-model="passwordForm.newPassword"
                    type="password"
                    label="新しいパスワード"
                    placeholder="新しいパスワードを入力"
                    required
                    :error="passwordErrors.newPassword"
                  />
                  
                  <BaseInput
                    v-model="passwordForm.confirmNewPassword"
                    type="password"
                    label="新しいパスワード確認"
                    placeholder="新しいパスワードを再入力"
                    required
                    :error="passwordErrors.confirmNewPassword"
                  />
                </div>
                
                <div class="mt-6">
                  <BaseButton
                    type="submit"
                    variant="secondary"
                    :loading="isPasswordLoading"
                    loading-text="変更中..."
                  >
                    パスワード変更
                  </BaseButton>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { BaseInput, BaseButton } from '@/components/ui'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const authStore = useAuthStore()

const user = computed(() => authStore.user)
const isLoading = ref(false)
const isPasswordLoading = ref(false)

const form = reactive({
  name: user.value?.name || '',
  email: user.value?.email || '',
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmNewPassword: '',
})

const errors = ref<Record<string, string>>({})
const passwordErrors = ref<Record<string, string>>({})
const passwordChangeSuccess = ref(false)

const validateProfile = () => {
  errors.value = {}
  
  if (!form.name.trim()) {
    errors.value.name = 'お名前が必要です'
  }
  
  if (!form.email) {
    errors.value.email = 'メールアドレスが必要です'
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.value.email = 'メールアドレスが無効です'
  }
  
  return Object.keys(errors.value).length === 0
}

const validatePassword = () => {
  passwordErrors.value = {}
  
  if (!passwordForm.currentPassword) {
    passwordErrors.value.currentPassword = '現在のパスワードが必要です'
  }
  
  if (!passwordForm.newPassword) {
    passwordErrors.value.newPassword = '新しいパスワードが必要です'
  } else if (passwordForm.newPassword.length < 6) {
    passwordErrors.value.newPassword = 'パスワードは6文字以上で入力してください'
  }
  
  if (!passwordForm.confirmNewPassword) {
    passwordErrors.value.confirmNewPassword = '新しいパスワードを確認してください'
  } else if (passwordForm.newPassword !== passwordForm.confirmNewPassword) {
    passwordErrors.value.confirmNewPassword = 'パスワードが一致しません'
  }
  
  return Object.keys(passwordErrors.value).length === 0
}

const handleUpdateProfile = async () => {
  if (!validateProfile()) return
  
  isLoading.value = true
  
  try {
    await authStore.updateProfile({
      name: form.name,
      email: form.email,
    })
    
    // Show success message
    console.log('Profile updated successfully')
  } catch (error) {
    console.error('Profile update failed:', error)
    errors.value.general = 'プロフィール更新に失敗しました。もう一度お試しください。'
  } finally {
    isLoading.value = false
  }
}

const handleChangePassword = async () => {
  if (!validatePassword()) return
  
  isPasswordLoading.value = true
  passwordErrors.value = {}
  passwordChangeSuccess.value = false
  
  try {
    const response = await authApi.changePassword({
      currentPassword: passwordForm.currentPassword,
      newPassword: passwordForm.newPassword,
    })
    
    if (response.success) {
      // Reset form on success
      passwordForm.currentPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmNewPassword = ''
      passwordChangeSuccess.value = true
      
      // 3秒後に成功メッセージを非表示
      setTimeout(() => {
        passwordChangeSuccess.value = false
      }, 3000)
    }
  } catch (error: any) {
    console.error('Password change failed:', error)
    
    // レスポンスからエラー情報を取得
    const errorDetail = error.response?.data?.detail || error.message
    const status = error.response?.status
    
    // HTTPステータスコードに基づくエラーハンドリング
    switch (status) {
      case 400:
        // バリデーションエラー
        if (errorDetail.includes('Incorrect current password')) {
          passwordErrors.value.currentPassword = '現在のパスワードが正しくありません'
        } else if (errorDetail.includes('must be different')) {
          passwordErrors.value.newPassword = '新しいパスワードは現在のパスワードと異なる必要があります'
        } else {
          passwordErrors.value.general = errorDetail
        }
        break
      
      case 401:
        // 認証エラー
        passwordErrors.value.general = 'セッションが期限切れです。再度ログインしてください。'
        // 3秒後にログイン画面へリダイレクト
        setTimeout(() => {
          authStore.logout()
        }, 3000)
        break
        
      case 422:
        // バリデーションエラー（フィールドレベル）
        if (error.response?.data?.detail?.errors) {
          const errors = error.response.data.detail.errors
          if (errors.currentPassword) {
            passwordErrors.value.currentPassword = errors.currentPassword[0]
          }
          if (errors.newPassword) {
            passwordErrors.value.newPassword = errors.newPassword[0]
          }
        } else {
          passwordErrors.value.general = 'パスワードは8文字以上で入力してください'
        }
        break
        
      case 500:
      case 502:
      case 503:
        // サーバーエラー
        passwordErrors.value.general = 'サーバーエラーが発生しました。しばらく待ってから再試行してください。'
        break
        
      default:
        // ネットワークエラーなど
        if (!navigator.onLine) {
          passwordErrors.value.general = 'インターネット接続を確認してください。'
        } else {
          passwordErrors.value.general = 'エラーが発生しました。もう一度お試しください。'
        }
    }
  } finally {
    isPasswordLoading.value = false
  }
}
</script>