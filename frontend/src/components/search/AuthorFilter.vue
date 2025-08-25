<template>
  <div class="author-filter" data-testid="author-filter">
    <label class="block text-sm font-medium text-gray-700 mb-2">
      作成者で絞り込み
    </label>

    <!-- Quick Filter: My Whiteboards -->
    <div class="mb-3">
      <button
        type="button"
        :class="[
          'inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md',
          isMyWhiteboardsSelected
            ? 'border-indigo-500 text-indigo-700 bg-indigo-50'
            : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
        ]"
        @click="toggleMyWhiteboards"
      >
        <svg
          class="-ml-0.5 mr-2 h-4 w-4"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 7V9C15 10.1 15.9 11 17 11V20C17 21.1 16.1 22 15 22H9C7.9 22 7 21.1 7 20V11C8.1 11 9 10.1 9 9V7H3V9C3 10.1 3.9 11 5 11V20C5 21.1 5.9 22 7 22H15C16.1 22 17 21.1 17 20V11C18.1 11 19 10.1 19 9Z" />
        </svg>
        自分のホワイトボード
      </button>
    </div>

    <!-- Author Selection -->
    <div class="relative">
      <Multiselect
        v-model="selectedAuthorIds"
        :options="authorOptions"
        :multiple="true"
        :searchable="true"
        :can-clear="true"
        :can-deselect="true"
        :close-on-select="false"
        :preserve-search="true"
        placeholder="作成者を選択..."
        no-results-text="該当する作成者がいません"
        no-options-text="利用可能な作成者がいません"
        :loading="searchStore.isLoadingOptions"
        :disabled="searchStore.isLoadingOptions"
        class="multiselect-custom"
        @change="handleAuthorChange"
      >
        <template #option="{ option }">
          <div class="flex items-center space-x-3">
            <!-- Avatar -->
            <div class="flex-shrink-0">
              <img
                v-if="option.avatar"
                :src="option.avatar"
                :alt="option.label"
                class="h-6 w-6 rounded-full object-cover"
              >
              <div
                v-else
                class="h-6 w-6 rounded-full bg-gray-300 flex items-center justify-center"
              >
                <span class="text-xs font-medium text-gray-700 uppercase">
                  {{ getInitials(option.label) }}
                </span>
              </div>
            </div>
            
            <!-- Name -->
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">
                {{ option.label }}
              </p>
              <p
                v-if="option.email"
                class="text-xs text-gray-500"
              >
                {{ option.email }}
              </p>
            </div>
          </div>
        </template>
        
        <template #tag="{ option, handleTagRemove }">
          <div class="inline-flex items-center space-x-2 bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
            <!-- Small Avatar -->
            <div class="flex-shrink-0">
              <img
                v-if="option.avatar"
                :src="option.avatar"
                :alt="option.label"
                class="h-4 w-4 rounded-full object-cover"
              >
              <div
                v-else
                class="h-4 w-4 rounded-full bg-blue-300 flex items-center justify-center"
              >
                <span class="text-xs font-medium text-blue-700 uppercase">
                  {{ getInitials(option.label) }}
                </span>
              </div>
            </div>
            
            <span>{{ option.label }}</span>
            <button 
              class="ml-1 text-blue-400 hover:text-blue-600"
              @click="(event) => handleTagRemove(option, event)"
            >
              <svg
                class="w-3 h-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </template>
      </Multiselect>
    </div>

    <!-- Selected Authors Count -->
    <div
      v-if="selectedAuthorIds.length > 0"
      class="mt-2 text-xs text-gray-500"
    >
      {{ selectedAuthorIds.length }}人の作成者を選択中 (OR検索)
    </div>

    <!-- Help Text -->
    <div class="mt-2 text-xs text-gray-500">
      複数選択した場合、いずれかの作成者によるホワイトボードが表示されます
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import Multiselect from '@vueform/multiselect'
import { useSearchStore } from '@/stores/search'
import { useAuthStore } from '@/stores/auth'

const searchStore = useSearchStore()
const authStore = useAuthStore()

// Convert authors to multiselect format
const authorOptions = computed(() => {
  return searchStore.availableAuthors.map(author => ({
    value: author.id,
    label: author.name,
    email: author.email,
    avatar: author.avatar
  }))
})

// Two-way binding with store
const selectedAuthorIds = computed({
  get: () => searchStore.filters.authors || [],
  set: (value) => {
    searchStore.updateFilters({ authors: value })
  }
})

// Check if "My Whiteboards" is selected
const isMyWhiteboardsSelected = computed(() => {
  return authStore.user && (searchStore.filters.authors || []).includes(authStore.user.id)
})

const handleAuthorChange = (value: string[] | string) => {
  // Multiselectコンポーネントから返される値が文字列の場合があるため、
  // 常に配列形式に正規化する（バックエンドAPI仕様に合わせるため）
  const arrayValue = Array.isArray(value) ? value : (value ? [value] : [])
  
  // 直接ストアを更新して循環参照を回避
  searchStore.updateFilters({ authors: arrayValue })
}

const toggleMyWhiteboards = () => {
  if (!authStore.user) return

  const currentUserId = authStore.user.id
  const currentAuthors = [...searchStore.filters.authors]

  if (isMyWhiteboardsSelected.value) {
    // Remove current user from selection
    const filteredAuthors = currentAuthors.filter(id => id !== currentUserId)
    searchStore.updateFilters({ authors: filteredAuthors })
  } else {
    // Add current user to selection (if not already there)
    if (!currentAuthors.includes(currentUserId)) {
      searchStore.updateFilters({ authors: [...currentAuthors, currentUserId] })
    }
  }
}

const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(part => part.charAt(0))
    .join('')
    .substring(0, 2)
}

// Load available authors on component mount
watch(() => (searchStore.availableAuthors || []).length, (newLength, oldLength) => {
  if (newLength === 0 && oldLength === 0) {
    searchStore.loadAvailableAuthors()
  }
})
</script>

<style>
/* Reuse the same multiselect styling as TagFilter */
.author-filter .multiselect-custom {
  --ms-font-size: 0.875rem;
  --ms-line-height: 1.25rem;
  --ms-border-color: #d1d5db;
  --ms-border-width: 1px;
  --ms-border-color-active: #2563eb;
  --ms-ring-width: 2px;
  --ms-ring-color: #93c5fd;
  --ms-placeholder-color: #9ca3af;
}

.author-filter .multiselect-custom.is-open {
  --ms-border-color: #2563eb;
}

.author-filter .multiselect-custom.is-disabled {
  --ms-bg: #f9fafb;
  --ms-border-color: #e5e7eb;
  opacity: 0.6;
}

/* Blue theme for author filter */
.author-filter .multiselect-option.is-pointed {
  --ms-option-bg: #dbeafe;
  --ms-option-color: #1e40af;
}

.author-filter .multiselect-option.is-selected {
  --ms-option-bg: #2563eb;
  --ms-option-color: #ffffff;
}

.author-filter .multiselect-spinner {
  --ms-spinner-color: #2563eb;
}

.author-filter .multiselect-tags {
  --ms-tag-bg: #dbeafe;
  --ms-tag-color: #1e40af;
  --ms-tag-radius: 9999px;
}
</style>