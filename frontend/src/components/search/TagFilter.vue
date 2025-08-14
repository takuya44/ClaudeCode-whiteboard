<template>
  <div class="tag-filter">
    <label class="block text-sm font-medium text-gray-700 mb-2">
      タグで絞り込み
    </label>
    
    <div class="relative">
      <Multiselect
        v-model="selectedTagIds"
        :options="tagOptions"
        :multiple="true"
        :searchable="true"
        :can-clear="true"
        :can-deselect="true"
        :close-on-select="false"
        :preserve-search="true"
        placeholder="タグを選択..."
        no-results-text="該当するタグがありません"
        no-options-text="利用可能なタグがありません"
        :loading="searchStore.isLoadingOptions"
        :disabled="searchStore.isLoadingOptions"
        class="multiselect-custom"
        @change="handleTagChange"
      >
        <template #option="{ option }">
          <div class="flex items-center space-x-2">
            <div 
              v-if="option.color" 
              class="w-3 h-3 rounded-full flex-shrink-0"
              :style="{ backgroundColor: option.color }"
            />
            <span class="flex-1">{{ option.label }}</span>
            <span
              v-if="option.usageCount"
              class="text-xs text-gray-500"
            >
              ({{ option.usageCount }})
            </span>
          </div>
        </template>
        
        <template #tag="{ option, handleTagRemove }">
          <div class="inline-flex items-center space-x-1 bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
            <div 
              v-if="option.color" 
              class="w-2 h-2 rounded-full"
              :style="{ backgroundColor: option.color }"
            />
            <span>{{ option.label }}</span>
            <button 
              class="ml-1 text-indigo-400 hover:text-indigo-600"
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

    <!-- Selected Tags Count -->
    <div
      v-if="selectedTagIds.length > 0"
      class="mt-2 text-xs text-gray-500"
    >
      {{ selectedTagIds.length }}個のタグを選択中 (AND検索)
    </div>

    <!-- Help Text -->
    <div class="mt-2 text-xs text-gray-500">
      複数選択した場合、すべてのタグを含むホワイトボードが表示されます
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import Multiselect from '@vueform/multiselect'
import { useSearchStore } from '@/stores/search'

const searchStore = useSearchStore()

// Convert tags to multiselect format
const tagOptions = computed(() => {
  return searchStore.availableTags.map(tag => ({
    value: tag.id,
    label: tag.name,
    color: tag.color,
    usageCount: tag.usageCount
  }))
})

// Two-way binding with store
const selectedTagIds = computed({
  get: () => searchStore.filters.tags || [],
  set: (value) => {
    searchStore.updateFilters({ tags: value })
  }
})

const handleTagChange = (value: string[]) => {
  selectedTagIds.value = value
}

// Load available tags on component mount
watch(() => (searchStore.availableTags || []).length, (newLength, oldLength) => {
  if (newLength === 0 && oldLength === 0) {
    searchStore.loadAvailableTags()
  }
})
</script>

<style>
/* Custom styling for multiselect */
.multiselect-custom {
  --ms-font-size: 0.875rem;
  --ms-line-height: 1.25rem;
  --ms-border-color: #d1d5db;
  --ms-border-width: 1px;
  --ms-border-color-active: #6366f1;
  --ms-ring-width: 2px;
  --ms-ring-color: #a5b4fc;
  --ms-placeholder-color: #9ca3af;
}

.multiselect-custom.is-open {
  --ms-border-color: #6366f1;
}

.multiselect-custom.is-disabled {
  --ms-bg: #f9fafb;
  --ms-border-color: #e5e7eb;
  opacity: 0.6;
}

/* Option styling */
.multiselect-option.is-pointed {
  --ms-option-bg: #eef2ff;
  --ms-option-color: #3730a3;
}

.multiselect-option.is-selected {
  --ms-option-bg: #6366f1;
  --ms-option-color: #ffffff;
}

/* Loading spinner */
.multiselect-spinner {
  --ms-spinner-color: #6366f1;
}

/* Tags styling */
.multiselect-tags {
  --ms-tag-bg: #eef2ff;
  --ms-tag-color: #3730a3;
  --ms-tag-radius: 9999px;
}

.multiselect-tags-search-wrapper {
  --ms-tags-search-bg: transparent;
}
</style>