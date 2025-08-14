<template>
  <div class="simple-multiselect relative">
    <!-- Selected items display -->
    <div 
      class="flex flex-wrap gap-1 p-2 border border-gray-300 rounded-md min-h-[2.5rem] cursor-text"
      @click="toggleDropdown"
    >
      <!-- Selected tags -->
      <span
        v-for="selectedValue in selectedValues"
        :key="selectedValue"
        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
      >
        {{ getDisplayLabel(selectedValue) }}
        <button
          class="ml-1 text-blue-400 hover:text-blue-600"
          @click.stop="removeItem(selectedValue)"
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
      </span>
      
      <!-- Placeholder or search input -->
      <input
        v-if="searchable"
        v-model="searchQuery"
        :placeholder="selectedValues.length === 0 ? placeholder : ''"
        class="flex-1 min-w-0 outline-none bg-transparent"
        @click.stop="openDropdown"
        @keydown.escape="closeDropdown"
      >
      <span
        v-else-if="selectedValues.length === 0"
        class="text-gray-400 text-sm"
      >
        {{ placeholder }}
      </span>
    </div>

    <!-- Dropdown -->
    <div
      v-if="isOpen"
      class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
    >
      <div
        v-if="filteredOptions.length === 0"
        class="px-3 py-2 text-sm text-gray-500"
      >
        {{ noOptionsText }}
      </div>
      <div
        v-for="option in filteredOptions"
        :key="option.value"
        class="px-3 py-2 text-sm cursor-pointer hover:bg-gray-100"
        :class="{ 'bg-blue-50': selectedValues.includes(option.value) }"
        @click="toggleOption(option.value)"
      >
        <slot
          name="option"
          :option="option"
        >
          {{ option.label }}
        </slot>
      </div>
    </div>

    <!-- Backdrop -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40"
      @click="closeDropdown"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Option {
  value: string
  label: string
  [key: string]: any
}

interface Props {
  modelValue: string[]
  options: Option[]
  placeholder?: string
  searchable?: boolean
  noOptionsText?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Select options...',
  searchable: true,
  noOptionsText: 'No options available'
})

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const isOpen = ref(false)
const searchQuery = ref('')

const selectedValues = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value) {
    return props.options
  }
  
  const query = searchQuery.value.toLowerCase()
  return props.options.filter(option =>
    option.label.toLowerCase().includes(query)
  )
})

const getDisplayLabel = (value: string): string => {
  const option = props.options.find(opt => opt.value === value)
  return option?.label || value
}

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const openDropdown = () => {
  isOpen.value = true
}

const closeDropdown = () => {
  isOpen.value = false
  searchQuery.value = ''
}

const toggleOption = (value: string) => {
  const currentValues = [...selectedValues.value]
  const index = currentValues.indexOf(value)
  
  if (index > -1) {
    currentValues.splice(index, 1)
  } else {
    currentValues.push(value)
  }
  
  selectedValues.value = currentValues
}

const removeItem = (value: string) => {
  const currentValues = selectedValues.value.filter(v => v !== value)
  selectedValues.value = currentValues
}

// Close dropdown when clicking outside
watch(isOpen, (newValue) => {
  if (newValue) {
    document.addEventListener('keydown', handleEscape)
  } else {
    document.removeEventListener('keydown', handleEscape)
  }
})

const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closeDropdown()
  }
}
</script>