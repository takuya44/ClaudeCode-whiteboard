<template>
  <div class="space-y-1">
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-gray-700"
    >
      {{ label }}
      <span
        v-if="required"
        class="text-red-500"
      >*</span>
    </label>
    
    <div class="relative">
      <div
        v-if="$slots['prefix-icon']"
        class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
      >
        <slot name="prefix-icon" />
      </div>
      
      <input
        :id="inputId"
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :min="min"
        :max="max"
        :step="step"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @keydown="handleKeydown"
      >
      
      <div
        v-if="$slots['suffix-icon']"
        class="absolute inset-y-0 right-0 pr-3 flex items-center"
      >
        <slot name="suffix-icon" />
      </div>
    </div>
    
    <div
      v-if="error || hint"
      class="text-sm"
    >
      <p
        v-if="error"
        class="text-red-600"
      >
        {{ error }}
      </p>
      <p
        v-else-if="hint"
        class="text-gray-500"
      >
        {{ hint }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, useId, useSlots } from 'vue'

interface Props {
  modelValue?: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
  label?: string
  placeholder?: string
  hint?: string
  error?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  min?: number | string
  max?: number | string
  step?: number | string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  required: false,
  size: 'md',
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  keydown: [event: KeyboardEvent]
}>()

const inputRef = ref<HTMLInputElement>()
const inputId = useId()
const slots = useSlots()

const baseClasses = 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed'

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-3 py-2 text-sm',
  lg: 'px-4 py-3 text-base',
}

const inputClasses = computed(() => {
  const classes = [baseClasses, sizeClasses[props.size]]
  
  if (props.error) {
    classes.push('border-red-300 focus:ring-red-500 focus:border-red-500')
  }
  
  if (slots['prefix-icon']) {
    classes.push('pl-10')
  }
  
  if (slots['suffix-icon']) {
    classes.push('pr-10')
  }
  
  return classes.join(' ')
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = props.type === 'number' ? Number(target.value) : target.value
  emit('update:modelValue', value)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

const focus = () => {
  inputRef.value?.focus()
}

const blur = () => {
  inputRef.value?.blur()
}

defineExpose({
  focus,
  blur,
})
</script>