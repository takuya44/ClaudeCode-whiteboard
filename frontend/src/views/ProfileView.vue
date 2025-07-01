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
  
  try {
    // TODO: Implement password change API call
    console.log('Password change request:', {
      currentPassword: passwordForm.currentPassword,
      newPassword: passwordForm.newPassword,
    })
    
    // Reset form on success
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmNewPassword = ''
    
    console.log('Password changed successfully')
  } catch (error) {
    console.error('Password change failed:', error)
    passwordErrors.value.general = 'パスワード変更に失敗しました。もう一度お試しください。'
  } finally {
    isPasswordLoading.value = false
  }
}
</script>