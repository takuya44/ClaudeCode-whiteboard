<template>
  <BaseModal
    :show="show"
    title="コラボレーター管理"
    size="lg"
    :loading="isLoading"
    hide-confirm-button
    cancel-text="閉じる"
    @close="handleClose"
    @cancel="handleClose"
  >
    <div class="space-y-6">
      <!-- ヘッダー情報 -->
      <div class="border-b border-gray-200 pb-4">
        <h3 class="text-lg font-medium text-gray-900">
          {{ whiteboard?.title }}
        </h3>
        <p class="text-sm text-gray-600 mt-1">
          現在のコラボレーター一覧を管理できます
        </p>
      </div>

      <!-- 検索・フィルター -->
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <BaseInput
            v-model="searchQuery"
            type="text"
            placeholder="名前またはメールアドレスで検索..."
            class="w-full"
          >
            <template #prefix-icon>
              <svg 
                class="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path 
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </template>
          </BaseInput>
        </div>
        <div class="w-full sm:w-48">
          <select
            v-model="permissionFilter"
            class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            <option value="all">
              すべての権限
            </option>
            <option value="view">
              表示のみ
            </option>
            <option value="edit">
              編集可能
            </option>
            <option value="admin">
              管理者
            </option>
          </select>
        </div>
      </div>

      <!-- コラボレーター一覧 -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <h4 class="text-sm font-medium text-gray-900">
            コラボレーター ({{ filteredCollaborators.length }}人)
          </h4>
          <button
            class="text-sm text-blue-600 hover:text-blue-500"
            @click="handleRefresh"
          >
            更新
          </button>
        </div>

        <!-- ローディング状態 -->
        <div 
          v-if="isLoading"
          class="flex items-center justify-center py-8"
        >
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>

        <!-- コラボレーターが存在しない場合 -->
        <div 
          v-else-if="filteredCollaborators.length === 0"
          class="text-center py-8"
        >
          <svg 
            class="w-12 h-12 text-gray-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path 
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
          <p class="text-gray-500 text-sm">
            {{ searchQuery ? '検索条件に一致するコラボレーターがいません' : 'コラボレーターがいません' }}
          </p>
        </div>

        <!-- コラボレーター一覧 -->
        <div 
          v-else
          class="space-y-2 max-h-96 overflow-y-auto"
        >
          <div
            v-for="collaborator in filteredCollaborators"
            :key="collaborator.user_id"
            class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div class="flex items-center space-x-3">
              <!-- アバター -->
              <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                <svg 
                  class="w-5 h-5 text-gray-600"
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

              <!-- ユーザー情報 -->
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ collaborator.user_name }}
                </p>
                <p class="text-sm text-gray-500 truncate">
                  {{ collaborator.user_email }}
                </p>
                <div class="flex items-center mt-1">
                  <span
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                    :class="getPermissionBadgeClass(collaborator.permission)"
                  >
                    {{ getPermissionLabel(collaborator.permission) }}
                  </span>
                  <span class="text-xs text-gray-400 ml-2">
                    {{ formatJoinedDate(collaborator.joined_at) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- アクション -->
            <div class="flex items-center space-x-2">
              <!-- 権限変更 -->
              <select
                :value="collaborator.permission"
                class="text-xs border border-gray-300 rounded px-2 py-1 focus:ring-primary-500 focus:border-primary-500"
                :disabled="isOwner(collaborator) || isProcessing"
                @change="handlePermissionChange(collaborator, $event)"
              >
                <option value="view">
                  表示のみ
                </option>
                <option value="edit">
                  編集可能
                </option>
                <option value="admin">
                  管理者
                </option>
              </select>

              <!-- 削除ボタン -->
              <button
                :disabled="isOwner(collaborator) || isProcessing"
                class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                @click="handleRemoveCollaborator(collaborator)"
              >
                <svg 
                  class="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path 
                    fill-rule="evenodd"
                    d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"
                    clip-rule="evenodd"
                  />
                  <path 
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- アクションボタン -->
      <div class="border-t border-gray-200 pt-4">
        <div class="flex justify-between">
          <button
            class="px-4 py-2 text-blue-600 hover:text-blue-500 text-sm font-medium"
            @click="$emit('openShare')"
          >
            新しいユーザーを招待
          </button>
          <div class="text-xs text-gray-500">
            最終更新: {{ lastUpdated }}
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

  <!-- 削除確認ダイアログ -->
  <BaseModal
    :show="showConfirmDialog"
    title="コラボレーターを削除"
    size="md"
    :loading="isProcessing"
    confirm-text="削除"
    cancel-text="キャンセル"
    @close="showConfirmDialog = false"
    @cancel="showConfirmDialog = false"
    @confirm="confirmRemoveCollaborator"
  >
    <div class="space-y-4">
      <p class="text-sm text-gray-700">
        <strong>{{ selectedCollaborator?.user_name }}</strong> をコラボレーターから削除しますか？
      </p>
      <p class="text-sm text-gray-600">
        この操作は取り消すことができません。削除されたユーザーはこのホワイトボードにアクセスできなくなります。
      </p>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import { useWhiteboardStore } from '@/stores/whiteboard'
import type { Whiteboard } from '@/types'

interface Props {
  show: boolean
  whiteboard: Whiteboard | null
}

interface Collaborator {
  user_id: string
  user_name: string
  user_email: string
  permission: 'view' | 'edit' | 'admin'
  joined_at: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  openShare: []
  collaboratorRemoved: [collaborator: Collaborator]
}>()

const whiteboardStore = useWhiteboardStore()

// State
const isLoading = ref(false)
const isProcessing = ref(false)
const error = ref('')
const collaborators = ref<Collaborator[]>([])
const searchQuery = ref('')
const permissionFilter = ref('all')
const showConfirmDialog = ref(false)
const selectedCollaborator = ref<Collaborator | null>(null)
const lastUpdated = ref('')

// Computed
const filteredCollaborators = computed(() => {
  let filtered = collaborators.value

  // 検索フィルター
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(collaborator =>
      collaborator.user_name.toLowerCase().includes(query) ||
      collaborator.user_email.toLowerCase().includes(query)
    )
  }

  // 権限フィルター
  if (permissionFilter.value !== 'all') {
    filtered = filtered.filter(collaborator =>
      collaborator.permission === permissionFilter.value
    )
  }

  return filtered
})

// Methods
const loadCollaborators = async () => {
  if (!props.whiteboard) return

  isLoading.value = true
  error.value = ''

  try {
    const result = await whiteboardStore.getCollaborators(props.whiteboard.id)
    // API response should match Collaborator interface, but handle type conversion if needed
    collaborators.value = result.map(user => ({
      user_id: user.id,
      user_name: user.name,
      user_email: user.email,
      permission: 'edit' as const, // Default permission, should come from API
      joined_at: user.createdAt || new Date().toISOString()
    }))
    lastUpdated.value = new Date().toLocaleTimeString()
  } catch (err) {
    console.error('Failed to load collaborators:', err)
    error.value = 'コラボレーターの読み込みに失敗しました'
  } finally {
    isLoading.value = false
  }
}

const handleRefresh = () => {
  loadCollaborators()
}

const handleRemoveCollaborator = (collaborator: Collaborator) => {
  selectedCollaborator.value = collaborator
  showConfirmDialog.value = true
}

const confirmRemoveCollaborator = async () => {
  if (!selectedCollaborator.value || !props.whiteboard) return

  isProcessing.value = true
  error.value = ''

  try {
    await whiteboardStore.removeCollaborator(
      props.whiteboard.id,
      selectedCollaborator.value.user_id
    )

    // ローカルからも削除
    collaborators.value = collaborators.value.filter(
      c => c.user_id !== selectedCollaborator.value!.user_id
    )

    emit('collaboratorRemoved', selectedCollaborator.value)
    showConfirmDialog.value = false
    selectedCollaborator.value = null
    lastUpdated.value = new Date().toLocaleTimeString()
  } catch (err) {
    console.error('Failed to remove collaborator:', err)
    error.value = 'コラボレーターの削除に失敗しました'
  } finally {
    isProcessing.value = false
  }
}

const handlePermissionChange = async (collaborator: Collaborator, event: Event) => {
  const target = event.target as HTMLSelectElement
  const newPermission = target.value as 'view' | 'edit' | 'admin'

  if (newPermission === collaborator.permission) return

  isProcessing.value = true
  error.value = ''

  try {
    // Note: 権限変更のAPIが実装されていないため、ここではローカル更新のみ
    // 実際のAPI実装時は以下のようなコードになる:
    // await whiteboardStore.updateCollaboratorPermission(
    //   props.whiteboard!.id,
    //   collaborator.user_id,
    //   newPermission
    // )

    // ローカル更新
    const index = collaborators.value.findIndex(c => c.user_id === collaborator.user_id)
    if (index !== -1) {
      collaborators.value[index].permission = newPermission
    }

    lastUpdated.value = new Date().toLocaleTimeString()
  } catch (err) {
    console.error('Failed to update permission:', err)
    error.value = '権限の変更に失敗しました'
    // エラー時は元の値に戻す
    target.value = collaborator.permission
  } finally {
    isProcessing.value = false
  }
}

const isOwner = (collaborator: Collaborator) => {
  return props.whiteboard?.ownerId === collaborator.user_id
}

const getPermissionLabel = (permission: string) => {
  switch (permission) {
    case 'view': return '表示のみ'
    case 'edit': return '編集可能'
    case 'admin': return '管理者'
    default: return permission
  }
}

const getPermissionBadgeClass = (permission: string) => {
  switch (permission) {
    case 'view':
      return 'bg-gray-100 text-gray-800'
    case 'edit':
      return 'bg-blue-100 text-blue-800'
    case 'admin':
      return 'bg-purple-100 text-purple-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatJoinedDate = (dateString: string) => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }) + ' 参加'
  } catch {
    return '参加日不明'
  }
}

const handleClose = () => {
  // リセット
  searchQuery.value = ''
  permissionFilter.value = 'all'
  error.value = ''
  
  emit('close')
}

// Watchers
watch(() => props.show, (newShow) => {
  if (newShow) {
    loadCollaborators()
  }
})

// Lifecycle
onMounted(() => {
  if (props.show) {
    loadCollaborators()
  }
})
</script>