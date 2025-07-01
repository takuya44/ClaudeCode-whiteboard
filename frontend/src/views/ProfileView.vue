<template>
  <DefaultLayout>
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-3xl mx-auto">
        <div class="bg-white shadow-soft rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h1 class="text-2xl font-bold text-gray-900">
              Profile Settings
            </h1>
            <p class="text-gray-600">
              Manage your account information and preferences.
            </p>
          </div>
          
          <div class="p-6 space-y-6">
            <form @submit.prevent="handleUpdateProfile">
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
                  label="Email Address"
                  placeholder="Enter your email"
                  required
                  :error="errors.email"
                />
              </div>
              
              <div class="mt-6">
                <BaseButton
                  type="submit"
                  :loading="isLoading"
                  loading-text="Updating..."
                >
                  Update Profile
                </BaseButton>
              </div>
            </form>
            
            <hr class="border-gray-200">
            
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-4">
                Change Password
              </h3>
              <form @submit.prevent="handleChangePassword">
                <div class="space-y-4">
                  <BaseInput
                    v-model="passwordForm.currentPassword"
                    type="password"
                    label="Current Password"
                    placeholder="Enter current password"
                    required
                    :error="passwordErrors.currentPassword"
                  />
                  
                  <BaseInput
                    v-model="passwordForm.newPassword"
                    type="password"
                    label="New Password"
                    placeholder="Enter new password"
                    required
                    :error="passwordErrors.newPassword"
                  />
                  
                  <BaseInput
                    v-model="passwordForm.confirmNewPassword"
                    type="password"
                    label="Confirm New Password"
                    placeholder="Confirm new password"
                    required
                    :error="passwordErrors.confirmNewPassword"
                  />
                </div>
                
                <div class="mt-6">
                  <BaseButton
                    type="submit"
                    variant="secondary"
                    :loading="isPasswordLoading"
                    loading-text="Changing..."
                  >
                    Change Password
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
    errors.value.name = 'Name is required'
  }
  
  if (!form.email) {
    errors.value.email = 'Email is required'
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.value.email = 'Email is invalid'
  }
  
  return Object.keys(errors.value).length === 0
}

const validatePassword = () => {
  passwordErrors.value = {}
  
  if (!passwordForm.currentPassword) {
    passwordErrors.value.currentPassword = 'Current password is required'
  }
  
  if (!passwordForm.newPassword) {
    passwordErrors.value.newPassword = 'New password is required'
  } else if (passwordForm.newPassword.length < 6) {
    passwordErrors.value.newPassword = 'Password must be at least 6 characters'
  }
  
  if (!passwordForm.confirmNewPassword) {
    passwordErrors.value.confirmNewPassword = 'Please confirm your new password'
  } else if (passwordForm.newPassword !== passwordForm.confirmNewPassword) {
    passwordErrors.value.confirmNewPassword = 'Passwords do not match'
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
    errors.value.general = 'Profile update failed. Please try again.'
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
    passwordErrors.value.general = 'Password change failed. Please try again.'
  } finally {
    isPasswordLoading.value = false
  }
}
</script>