<template>
  <BaseModal
    :show="show"
    title="ホワイトボードを共有"
    size="lg"
    :loading="isLoading"
    confirm-text="共有"
    cancel-text="キャンセル"
    @close="handleClose"
    @cancel="handleClose"
    @confirm="handleShare"
  >
    <div class="space-y-6">
      <!-- 共有設定 -->
      <div class="space-y-4">
        <div>
          <h4 class="text-sm font-medium text-gray-900 mb-3">
            共有設定
          </h4>
          <div class="space-y-3">
            <label class="flex items-center">
              <input
                v-model="shareSettings.permission"
                type="radio"
                value="view"
                class="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
              >
              <span class="ml-2 text-sm text-gray-700">
                表示のみ
                <span class="text-gray-500">（閲覧のみ可能）</span>
              </span>
            </label>
            <label class="flex items-center">
              <input
                v-model="shareSettings.permission"
                type="radio"
                value="edit"
                class="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
              >
              <span class="ml-2 text-sm text-gray-700">
                編集可能
                <span class="text-gray-500">（描画・編集が可能）</span>
              </span>
            </label>
            <label class="flex items-center">
              <input
                v-model="shareSettings.permission"
                type="radio"
                value="admin"
                class="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
              >
              <span class="ml-2 text-sm text-gray-700">
                管理者
                <span class="text-gray-500">（すべての権限）</span>
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- ユーザー追加 -->
      <div class="space-y-4">
        <div>
          <h4 class="text-sm font-medium text-gray-900 mb-3">
            ユーザーを追加
          </h4>
          <div class="flex space-x-2">
            <BaseInput
              v-model="newUserEmail"
              type="email"
              placeholder="example@email.com"
              class="flex-1"
              :error="emailError"
              @keydown.enter="handleAddUser"
            />
            <BaseButton
              variant="outline"
              :disabled="!newUserEmail || !!emailError"
              @click="handleAddUser"
            >
              追加
            </BaseButton>
          </div>
        </div>

        <!-- 追加されたユーザー一覧 -->
        <div 
          v-if="shareSettings.userEmails.length > 0"
          class="space-y-2"
        >
          <h5 class="text-sm font-medium text-gray-900">
            共有予定のユーザー
          </h5>
          <div class="max-h-32 overflow-y-auto">
            <div
              v-for="(email, index) in shareSettings.userEmails"
              :key="email"
              class="flex items-center justify-between p-2 bg-gray-50 rounded-md"
            >
              <div class="flex items-center space-x-2">
                <div class="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
                  <svg 
                    class="w-3 h-3 text-gray-600" 
                    fill="currentColor" 
                    viewBox="0 0 20 20"
                  >
                    <path 
                      fill-rule="evenodd" 
                      d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" 
                      clip-rule="evenodd" 
                    />
                  </svg>
                </div>
                <span class="text-sm text-gray-700">{{ email }}</span>
              </div>
              <button
                class="text-red-500 hover:text-red-700 p-1 rounded-md hover:bg-red-50"
                @click="removeUser(index)"
              >
                <svg 
                  class="w-4 h-4" 
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path 
                    fill-rule="evenodd" 
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
                    clip-rule="evenodd" 
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 共有結果 -->
      <div 
        v-if="shareResult" 
        class="space-y-3"
      >
        <h5 class="text-sm font-medium text-gray-900">
          共有結果
        </h5>
        <div class="space-y-2">
          <div
            v-for="result in shareResult.results"
            :key="result.email"
            class="flex items-center justify-between p-2 rounded-md"
            :class="result.success ? 'bg-green-50' : 'bg-red-50'"
          >
            <div class="flex items-center space-x-2">
              <div
                class="w-5 h-5 rounded-full flex items-center justify-center"
                :class="result.success ? 'bg-green-100' : 'bg-red-100'"
              >
                <svg
                  class="w-3 h-3"
                  :class="result.success ? 'text-green-600' : 'text-red-600'"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    v-if="result.success"
                    fill-rule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clip-rule="evenodd"
                  />
                  <path
                    v-else
                    fill-rule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
              <span class="text-sm text-gray-700">{{ result.email }}</span>
            </div>
            <span
              class="text-xs px-2 py-1 rounded-full"
              :class="result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
            >
              {{ result.success ? '成功' : result.error }}
            </span>
          </div>
        </div>
      </div>

      <!-- エラーメッセージ -->
      <div 
        v-if="error" 
        class="p-3 bg-red-50 border border-red-200 rounded-md"
      >
        <div class="flex">
          <svg 
            class="w-5 h-5 text-red-400" 
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path 
              fill-rule="evenodd" 
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" 
              clip-rule="evenodd" 
            />
          </svg>
          <div class="ml-2">
            <p class="text-sm text-red-700">
              {{ error }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { whiteboardApi } from '@/api/whiteboard'
import type { Whiteboard } from '@/types'

interface Props {
  show: boolean
  whiteboard: Whiteboard | null
}

interface ShareResult {
  results: Array<{
    email: string
    success: boolean
    error?: string
  }>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  shared: [results: ShareResult]
}>()

const isLoading = ref(false)
const error = ref('')
const newUserEmail = ref('')
const shareResult = ref<ShareResult | null>(null)

const shareSettings = ref({
  permission: 'edit' as 'view' | 'edit' | 'admin',
  userEmails: [] as string[],
})

const emailError = computed(() => {
  if (!newUserEmail.value) return ''
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(newUserEmail.value)) {
    return 'メールアドレスの形式が正しくありません'
  }
  
  if (shareSettings.value.userEmails.includes(newUserEmail.value)) {
    return 'このメールアドレスは既に追加されています'
  }
  
  return ''
})

const handleAddUser = () => {
  if (!newUserEmail.value || emailError.value) return
  
  shareSettings.value.userEmails.push(newUserEmail.value)
  newUserEmail.value = ''
}

const removeUser = (index: number) => {
  shareSettings.value.userEmails.splice(index, 1)
}

const handleShare = async () => {
  if (!props.whiteboard || shareSettings.value.userEmails.length === 0) {
    error.value = '共有するユーザーを追加してください'
    return
  }

  isLoading.value = true
  error.value = ''
  shareResult.value = null

  try {
    const response = await whiteboardApi.shareWhiteboard(
      props.whiteboard.id,
      shareSettings.value.userEmails
    )

    if (response.success) {
      // API響応に基づいて結果を構築
      shareResult.value = {
        results: shareSettings.value.userEmails.map(email => ({
          email,
          success: true
        }))
      }
      
      emit('shared', shareResult.value)
      
      // 成功時は少し待ってから閉じる
      setTimeout(() => {
        handleClose()
      }, 2000)
    } else {
      error.value = response.message || '共有に失敗しました'
    }
  } catch (err) {
    console.error('Share whiteboard error:', err)
    error.value = '共有処理でエラーが発生しました'
  } finally {
    isLoading.value = false
  }
}

const handleClose = () => {
  // リセット
  shareSettings.value = {
    permission: 'edit',
    userEmails: [],
  }
  newUserEmail.value = ''
  error.value = ''
  shareResult.value = null
  
  emit('close')
}

// ダイアログが開いたときにリセット
watch(() => props.show, (newShow) => {
  if (newShow) {
    shareSettings.value = {
      permission: 'edit',
      userEmails: [],
    }
    newUserEmail.value = ''
    error.value = ''
    shareResult.value = null
  }
})
</script>