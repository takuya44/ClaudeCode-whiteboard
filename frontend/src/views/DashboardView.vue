<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">
        お帰りなさい、{{ user?.name || 'ユーザー' }}さん！
      </h1>
      <p class="text-gray-600">
        ホワイトボードを管理し、コラボレーションを開始しましょう。
      </p>
    </div>

    <div class="mb-6 flex flex-col sm:flex-row gap-4">
      <div class="flex-1 max-w-md">
        <BaseInput
          v-model="searchQuery"
          type="search"
          placeholder="ホワイトボードを検索..."
          @input="handleSearch"
        >
          <template #prefix-icon>
            <svg
              class="w-5 h-5 text-gray-400"
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
      
      <BaseButton @click="showCreateModal = true">
        <template #icon-left>
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
        </template>
        新しいホワイトボードを作成
      </BaseButton>
    </div>

    <div
      v-if="isLoading"
      class="flex justify-center items-center py-12"
    >
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
    </div>

    <div
      v-else-if="!whiteboards || whiteboards.length === 0"
      class="text-center py-12"
    >
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          v-if="searchQuery"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
        <path
          v-else
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">
        {{ searchQuery ? '検索結果が見つかりません' : 'ホワイトボードがありません' }}
      </h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ searchQuery 
          ? `"${searchQuery}" に一致するホワイトボードが見つかりませんでした。` 
          : '最初のホワイトボードを作成して始めましょう。' }}
      </p>
      <button
        v-if="searchQuery"
        class="mt-4 text-sm text-primary-600 hover:text-primary-500"
        @click="clearSearch"
      >
        検索をクリア
      </button>
    </div>

    <div
      v-else
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      <div
        v-for="whiteboard in (whiteboards || [])"
        :key="whiteboard.id"
        class="bg-white rounded-lg shadow-soft hover:shadow-medium transition-shadow cursor-pointer relative group"
        @click="openWhiteboard(whiteboard.id)"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-2">
            <h3 class="text-lg font-semibold text-gray-900 flex-1">
              {{ whiteboard.title }}
            </h3>
            <button
              v-if="whiteboard.ownerId === user?.id"
              class="opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-600 ml-2"
              title="削除"
              @click="handleDeleteClick($event, whiteboard as Whiteboard)"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
          <p
            v-if="whiteboard.description"
            class="text-gray-600 mb-4"
          >
            {{ whiteboard.description }}
          </p>
          <div class="flex items-center justify-between text-sm text-gray-500">
            <span>{{ formatDate(whiteboard.updatedAt) }}</span>
            <span
              v-if="whiteboard.isPublic"
              class="text-green-600"
            >公開</span>
            <span
              v-else
              class="text-gray-600"
            >非公開</span>
          </div>
        </div>
      </div>
    </div>

    <BaseModal
      :show="showCreateModal"
      title="新しいホワイトボードを作成"
      @close="showCreateModal = false"
      @cancel="showCreateModal = false"
      @confirm="handleCreateWhiteboard"
    >
      <div class="space-y-4">
        <BaseInput
          v-model="newWhiteboard.title"
          label="タイトル"
          placeholder="ホワイトボードのタイトルを入力"
          required
        />
        
        <BaseInput
          v-model="newWhiteboard.description"
          label="説明（任意）"
          placeholder="説明を入力"
        />
        
        <div class="flex items-center">
          <input
            id="is-public"
            v-model="newWhiteboard.isPublic"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          >
          <label
            for="is-public"
            class="ml-2 block text-sm text-gray-900"
          >
            このホワイトボードを公開する
          </label>
        </div>
      </div>
    </BaseModal>

    <WhiteboardDeleteDialog
      :show="showDeleteDialog"
      :whiteboard-id="whiteboardToDelete?.id || ''"
      :whiteboard-title="whiteboardToDelete?.title || ''"
      :collaborator-count="whiteboardToDelete?.collaboratorCount"
      @close="showDeleteDialog = false"
      @deleted="handleDeleteWhiteboard"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWhiteboardStore } from '@/stores/whiteboard'
import { BaseButton, BaseModal, BaseInput } from '@/components/ui'
import WhiteboardDeleteDialog from '@/components/whiteboard/WhiteboardDeleteDialog.vue'
import type { Whiteboard } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const whiteboardStore = useWhiteboardStore()

const showCreateModal = ref(false)
const showDeleteDialog = ref(false)
const whiteboardToDelete = ref<{ id: string; title: string; collaboratorCount?: number } | null>(null)
const searchQuery = ref('')
const searchDebounceTimer = ref<number | null>(null)

const newWhiteboard = reactive({
  title: '',
  description: '',
  isPublic: false
})

const user = computed(() => authStore.user)
const whiteboards = computed(() => whiteboardStore.whiteboards || [])
const isLoading = computed(() => whiteboardStore.isLoading || whiteboardStore.isSearching)

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const openWhiteboard = (id: string) => {
  router.push(`/app/whiteboard/${id}`)
}

const handleCreateWhiteboard = async () => {
  if (!newWhiteboard.title.trim()) return
  
  try {
    await whiteboardStore.createWhiteboard({
      title: newWhiteboard.title,
      description: newWhiteboard.description,
      isPublic: newWhiteboard.isPublic
    })
    
    showCreateModal.value = false
    newWhiteboard.title = ''
    newWhiteboard.description = ''
    newWhiteboard.isPublic = false
  } catch (error) {
    console.error('Failed to create whiteboard:', error)
  }
}

const handleDeleteClick = (event: Event, whiteboard: Whiteboard) => {
  event.stopPropagation()
  whiteboardToDelete.value = {
    id: whiteboard.id,
    title: whiteboard.title,
    collaboratorCount: whiteboard.collaborators?.length || 0
  }
  showDeleteDialog.value = true
}

const handleDeleteWhiteboard = async () => {
  // 削除処理は削除ダイアログ内で完結するため、成功時のみダイアログを閉じる
  showDeleteDialog.value = false
  whiteboardToDelete.value = null
  // ホワイトボード一覧を再取得
  await whiteboardStore.fetchWhiteboards()
}

const handleSearch = () => {
  // デバウンスタイマーをクリア
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value)
  }
  
  // 新しいデバウンスタイマーを設定（300ms）
  searchDebounceTimer.value = window.setTimeout(async () => {
    if (searchQuery.value.trim()) {
      await whiteboardStore.searchWhiteboards(searchQuery.value.trim())
    } else {
      // 検索クエリが空の場合は通常の一覧を取得
      await whiteboardStore.fetchWhiteboards()
    }
  }, 300)
}

const clearSearch = async () => {
  searchQuery.value = ''
  await whiteboardStore.clearSearch()
}

onMounted(async () => {
  try {
    await whiteboardStore.fetchWhiteboards()
  } catch (error) {
    console.error('Failed to load whiteboards:', error)
    // Error is already handled in store, no need to throw
  }
})
</script>