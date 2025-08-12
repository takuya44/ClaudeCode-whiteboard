<template>
  <div 
    class="result-card bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
    tabindex="0"
    role="button"
    :aria-label="`ホワイトボード「${whiteboard.title}」を開く`"
    @click="navigateToWhiteboard"
    @keydown.enter="navigateToWhiteboard"
    @keydown.space.prevent="navigateToWhiteboard"
  >
    <!-- Header -->
    <div class="p-4 border-b border-gray-100">
      <div class="flex items-start justify-between">
        <div class="flex-1 min-w-0">
          <h3 class="text-lg font-semibold text-gray-900 truncate">
            {{ whiteboard.title }}
          </h3>
          <p
            v-if="whiteboard.description"
            class="mt-1 text-sm text-gray-600 line-clamp-2"
          >
            {{ whiteboard.description }}
          </p>
        </div>
        
        <!-- Visibility Icon -->
        <div class="ml-3 flex-shrink-0">
          <div
            :title="whiteboard.isPublic ? 'パブリック' : 'プライベート'"
            :class="[
              'inline-flex items-center justify-center w-8 h-8 rounded-full',
              whiteboard.isPublic
                ? 'bg-green-100 text-green-600'
                : 'bg-gray-100 text-gray-600'
            ]"
          >
            <svg
              v-if="whiteboard.isPublic"
              class="w-4 h-4"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
            </svg>
            <svg
              v-else
              class="w-4 h-4"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Creator Info -->
    <div class="p-4">
      <div class="flex items-center space-x-3">
        <!-- Avatar -->
        <div class="flex-shrink-0">
          <img
            v-if="whiteboard.creator.avatar"
            :src="whiteboard.creator.avatar"
            :alt="whiteboard.creator.name"
            class="h-8 w-8 rounded-full object-cover"
          >
          <div
            v-else
            class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center"
          >
            <span class="text-sm font-medium text-gray-700">
              {{ getInitials(whiteboard.creator.name) }}
            </span>
          </div>
        </div>
        
        <!-- Creator Name -->
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900">
            {{ whiteboard.creator.name }}
          </p>
          <div class="flex items-center space-x-4 text-xs text-gray-500 mt-1">
            <!-- Creation Date -->
            <div class="flex items-center">
              <svg
                class="w-3 h-3 mr-1"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z" />
              </svg>
              {{ formatDate(whiteboard.createdAt) }}
            </div>
            
            <!-- Update Date -->
            <div class="flex items-center">
              <svg
                class="w-3 h-3 mr-1"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M9 11H7v6h2v-6zm4 0h-2v6h2v-6zm4 0h-2v6h2v-6zm2-7h-3V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H5V9h14v11z" />
              </svg>
              {{ formatDate(whiteboard.updatedAt) }}
            </div>
            
            <!-- Collaborators -->
            <div
              v-if="whiteboard.collaboratorCount > 0"
              class="flex items-center"
            >
              <svg
                class="w-3 h-3 mr-1"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M16 4c0-1.11.89-2 2-2s2 .89 2 2-.89 2-2 2-2-.89-2-2zM4 18v-4h3v4H4zM18 8.5V7c0-1.11-.89-2-2-2s-2 .89-2 2v1.5c0 1.11.89 2 2 2s2-.89 2-2zM8 12.5V11c0-1.11-.89-2-2-2s-2 .89-2 2v1.5c0 1.11.89 2 2 2s2-.89 2-2zM8 18v-4h3v4H8zM16 18v-4h3v4h-3z" />
              </svg>
              +{{ whiteboard.collaboratorCount }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tags -->
    <div
      v-if="(whiteboard.tags || []).length > 0"
      class="px-4 pb-4"
    >
      <div class="flex flex-wrap gap-2">
        <span
          v-for="tag in visibleTags"
          :key="tag.id"
          :style="{ backgroundColor: tag.color || '#e5e7eb', color: getContrastColor(tag.color || '#e5e7eb') }"
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
        >
          {{ tag.name }}
        </span>
        
        <!-- Show more tags indicator -->
        <span
          v-if="(whiteboard.tags || []).length > maxVisibleTags"
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600"
          :title="`他 ${(whiteboard.tags || []).length - maxVisibleTags} 個のタグ`"
        >
          +{{ (whiteboard.tags || []).length - maxVisibleTags }}
        </span>
      </div>
    </div>

    <!-- Keyboard focus indicator -->
    <div
      class="absolute inset-0 rounded-lg ring-2 ring-offset-2 ring-indigo-500 opacity-0 transition-opacity focus-within:opacity-100"
      aria-hidden="true"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { WhiteboardSearchResult } from '@/types/search'

interface Props {
  whiteboard: WhiteboardSearchResult
  maxVisibleTags?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxVisibleTags: 3
})

const router = useRouter()

// Show only first few tags to prevent UI overflow
const visibleTags = computed(() => {
  return (props.whiteboard.tags || []).slice(0, props.maxVisibleTags)
})

const navigateToWhiteboard = () => {
  // ルート名を使用した方法（保守性が高い）
  router.push({ name: 'Whiteboard', params: { id: props.whiteboard.id } })
}

const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(part => part.charAt(0))
    .join('')
    .substring(0, 2)
    .toUpperCase()
}

const formatDate = (date: Date): string => {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return '今日'
  } else if (diffDays === 1) {
    return '昨日'
  } else if (diffDays < 7) {
    return `${diffDays}日前`
  } else if (diffDays < 30) {
    return `${Math.floor(diffDays / 7)}週間前`
  } else if (diffDays < 365) {
    return `${Math.floor(diffDays / 30)}ヶ月前`
  } else {
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}

// Get contrasting text color based on background color
const getContrastColor = (hexColor: string): string => {
  // Remove # if present
  const color = hexColor.replace('#', '')
  
  // Parse r, g, b values
  const r = parseInt(color.substring(0, 2), 16)
  const g = parseInt(color.substring(2, 4), 16)
  const b = parseInt(color.substring(4, 6), 16)
  
  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  
  // Return black or white based on luminance
  return luminance > 0.5 ? '#000000' : '#ffffff'
}
</script>

<style scoped>
.result-card {
  position: relative;
}

.result-card:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .result-card {
    transition: none;
  }
}
</style>