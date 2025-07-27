<template>
  <BaseModal
    :show="show"
    title="ホワイトボードを削除"
    size="md"
    :loading="isDeleting"
    confirm-text="削除"
    cancel-text="キャンセル"
    :confirm-disabled="!isDeleteConfirmed"
    @close="handleClose"
    @cancel="handleClose"
    @confirm="handleDelete"
  >
    <div class="space-y-4">
      <p class="text-sm text-gray-700">
        <strong>{{ whiteboardTitle }}</strong> を削除しますか？
      </p>
      <p class="text-sm text-gray-600">
        この操作は取り消すことができません。削除されたホワイトボードは復元できません。
      </p>
      <p
        v-if="collaboratorCount && collaboratorCount > 0"
        class="text-sm text-red-600 font-medium"
      >
        ⚠️ このホワイトボードには {{ collaboratorCount }} 人のコラボレーターがいます。削除すると全員がアクセスできなくなります。
      </p>
      
      <!-- 削除確認のための名前入力 -->
      <div class="mt-4">
        <label
          for="confirm-title"
          class="block text-sm font-medium text-gray-700 mb-2"
        >
          確認のため、ホワイトボード名を入力してください:
        </label>
        <input
          id="confirm-title"
          v-model="confirmTitle"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          :placeholder="whiteboardTitle"
          @keyup.enter="handleDelete"
        >
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useWhiteboardStore } from '@/stores/whiteboard'
import { useToast } from '@/composables/useToast'
import BaseModal from '@/components/ui/BaseModal.vue'

interface Props {
  show: boolean
  whiteboardId: string
  whiteboardTitle: string
  collaboratorCount?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  deleted: []
  error: [error: Error]
}>()

const whiteboardStore = useWhiteboardStore()
const { showError } = useToast()

const isDeleting = ref(false)
const confirmTitle = ref('')

// 削除確認: タイトルが一致しているかチェック
const isDeleteConfirmed = computed(() => {
  return confirmTitle.value === props.whiteboardTitle
})

// ダイアログが開かれたときにリセット
watch(() => props.show, (newVal) => {
  if (newVal) {
    confirmTitle.value = ''
  }
})

const handleClose = () => {
  confirmTitle.value = ''
  emit('close')
}

const handleDelete = async () => {
  if (!isDeleteConfirmed.value) return
  
  isDeleting.value = true
  try {
    await whiteboardStore.deleteWhiteboard(props.whiteboardId)
    emit('deleted')
  } catch (error) {
    console.error('Failed to delete whiteboard:', error)
    
    // エラーメッセージの詳細化
    let errorMessage = 'ホワイトボードの削除に失敗しました'
    if (error instanceof Error) {
      if (error.message.includes('404')) {
        errorMessage = 'ホワイトボードが見つかりません'
      } else if (error.message.includes('403')) {
        errorMessage = 'このホワイトボードを削除する権限がありません'
      } else if (error.message.includes('500')) {
        errorMessage = 'サーバーエラーが発生しました。しばらくしてから再度お試しください'
      }
    }
    
    showError(errorMessage)
    emit('error', error as Error)
  } finally {
    isDeleting.value = false
  }
}
</script>