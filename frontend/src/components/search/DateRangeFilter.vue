<template>
  <div class="date-range-filter" data-testid="date-range-filter">
    <label class="block text-sm font-medium text-gray-700 mb-2">
      日付範囲で絞り込み
    </label>

    <!-- Date Type Toggle -->
    <div class="mb-3">
      <div class="flex rounded-md border border-gray-300 p-1 bg-gray-50">
        <button
          :class="[
            'flex-1 px-3 py-1 text-sm font-medium rounded transition-colors',
            currentDateType === 'created'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          ]"
          @click="setDateType('created')"
        >
          作成日
        </button>
        <button
          :class="[
            'flex-1 px-3 py-1 text-sm font-medium rounded transition-colors',
            currentDateType === 'updated'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          ]"
          @click="setDateType('updated')"
        >
          更新日
        </button>
      </div>
    </div>

    <!-- Quick Presets -->
    <div class="mb-4">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="preset in datePresets"
          :key="preset.label"
          type="button"
          :class="[
            'px-3 py-1 text-xs border rounded-full transition-colors',
            isPresetActive(preset)
              ? 'border-green-500 bg-green-50 text-green-700'
              : 'border-gray-300 text-gray-600 hover:bg-gray-50'
          ]"
          @click="applyPreset(preset)"
        >
          {{ preset.label }}
        </button>
      </div>
    </div>

    <!-- Date Range Picker -->
    <div class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">開始日</label>
        <input
          type="date"
          data-testid="start-date-input"
          :value="startDate ? startDate.toISOString().split('T')[0] : ''"
          :max="endDate ? endDate.toISOString().split('T')[0] : undefined"
          class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
          @change="(e) => startDate = (e.target as HTMLInputElement).value ? new Date((e.target as HTMLInputElement).value) : null"
        >
      </div>

      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">終了日</label>
        <input
          type="date"
          data-testid="end-date-input"
          :value="endDate ? endDate.toISOString().split('T')[0] : ''"
          :min="startDate ? startDate.toISOString().split('T')[0] : undefined"
          class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
          @change="(e) => endDate = (e.target as HTMLInputElement).value ? new Date((e.target as HTMLInputElement).value) : null"
        >
      </div>
    </div>

    <!-- Validation Error -->
    <div
      v-if="validationError"
      class="mt-2 text-xs text-red-600"
    >
      {{ validationError }}
    </div>

    <!-- Clear Button -->
    <div
      v-if="hasDateRange"
      class="mt-3"
    >
      <button
        type="button"
        class="text-xs text-gray-500 hover:text-gray-700 underline"
        @click="clearDateRange"
      >
        日付範囲をクリア
      </button>
    </div>

    <!-- Help Text -->
    <div class="mt-2 text-xs text-gray-500">
      {{ currentDateType === 'created' ? '作成日' : '更新日' }}を基準に検索します
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useSearchStore } from '@/stores/search'
import type { DatePreset } from '@/types/search'

const searchStore = useSearchStore()

const validationError = ref<string | null>(null)

// ストアとの双方向バインディング
// storeのdateRangeを直接参照し、nullチェックを適切に行う
const dateRange = computed(() => searchStore.filters.dateRange)

// UI表示用の現在の日付タイプ（computed使用で安全な実装）
const currentDateType = computed(() => {
  return searchStore.filters.dateRange?.type || 'created'
})

const startDate = computed({
  get: () => searchStore.filters.dateRange?.start ?? null,
  set: (value: Date | null) => {
    updateDateRange({ start: value })
  }
})

const endDate = computed({
  get: () => searchStore.filters.dateRange?.end ?? null,
  set: (value: Date | null) => {
    updateDateRange({ end: value })
  }
})

const hasDateRange = computed(() => {
  return dateRange.value && (dateRange.value.start !== null || dateRange.value.end !== null)
})

// Date presets - シンプルな配列に戻す
const datePresets: DatePreset[] = [
  {
    label: '今日',
    value: () => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      return {
        start: today,
        end: tomorrow,
        type: 'created'
      }
    }
  },
  {
    label: '過去7日',
    value: () => {
      const end = new Date()
      end.setHours(23, 59, 59, 999)
      const start = new Date()
      start.setDate(start.getDate() - 6)
      start.setHours(0, 0, 0, 0)
      return {
        start,
        end,
        type: 'created'
      }
    }
  },
  {
    label: '今月',
    value: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth(), 1)
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999)
      return {
        start,
        end,
        type: 'created'
      }
    }
  },
  {
    label: '先月',
    value: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth() - 1, 1)
      const end = new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59, 999)
      return {
        start,
        end,
        type: 'created'
      }
    }
  }
]

const updateDateRange = (updates: { start?: Date | null; end?: Date | null }) => {
  const newDateRange = {
    start: updates.start !== undefined ? updates.start : (searchStore.filters.dateRange?.start ?? null),
    end: updates.end !== undefined ? updates.end : (searchStore.filters.dateRange?.end ?? null),
    type: searchStore.filters.dateRange?.type || 'created' as const
  }
  
  // Validate date range
  if (newDateRange.start && newDateRange.end && newDateRange.start > newDateRange.end) {
    validationError.value = '終了日は開始日より後の日付を選択してください'
    return
  }
  
  validationError.value = null
  searchStore.updateFilters({ dateRange: newDateRange })
}

const setDateType = (type: 'created' | 'updated') => {
  searchStore.updateFilters({
    dateRange: {
      start: searchStore.filters.dateRange?.start || null,
      end: searchStore.filters.dateRange?.end || null,
      type
    }
  })
}

// 各プリセットのアクティブ状態を個別に管理
const activePreset = ref<string | null>(null)

const isPresetActive = (preset: DatePreset): boolean => {
  return activePreset.value === preset.label
}

// プリセット適用時にアクティブ状態を更新
const applyPreset = (preset: DatePreset) => {
  const presetValue = preset.value()
  activePreset.value = preset.label
  searchStore.updateFilters({ dateRange: presetValue })
}


const clearDateRange = () => {
  searchStore.updateFilters({
    dateRange: {
      start: null,
      end: null,
      type: searchStore.filters.dateRange?.type || 'created'
    }
  })
  // バリデーションエラーもクリア
  validationError.value = null
  // プリセットもリセット
  activePreset.value = null
}


</script>

<style>
/* Date picker custom styling */
.date-range-filter .dp__input {
  @apply border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm;
  @apply focus:outline-none focus:ring-green-500 focus:border-green-500;
}

.date-range-filter .dp__input_focus {
  @apply ring-2 ring-green-500 border-green-500;
}

.date-range-filter .dp__calendar {
  @apply border border-gray-200 rounded-lg shadow-lg;
}

.date-range-filter .dp__calendar_header {
  @apply border-b border-gray-200;
}

.date-range-filter .dp__calendar_row {
  @apply border-b border-gray-100;
}

.date-range-filter .dp__date_hover:not(.dp__date_disabled) {
  @apply bg-green-50 text-green-800;
}

.date-range-filter .dp__date_selected {
  @apply bg-green-500 text-white;
}

.date-range-filter .dp__date_selected:hover {
  @apply bg-green-600;
}

.date-range-filter .dp__today {
  @apply border border-green-500;
}
</style>