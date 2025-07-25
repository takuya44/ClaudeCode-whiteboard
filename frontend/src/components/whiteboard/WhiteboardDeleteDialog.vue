<template>
  <BaseModal
    :show="show"
    title="ホワイトボードを削除"
    size="md"
    :loading="isDeleting"
    confirm-text="削除"
    cancel-text="キャンセル"
    @close="$emit('close')"
    @cancel="$emit('close')"
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
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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
}>()

const isDeleting = ref(false)

const handleDelete = async () => {
  isDeleting.value = true
  try {
    emit('deleted')
  } finally {
    isDeleting.value = false
  }
}
</script>