<template>
  <Teleport to="body">
    <Transition
      enter-active-class="duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click="handleBackdropClick"
      >
        <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
          
          <Transition
            enter-active-class="duration-300 ease-out"
            enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to-class="opacity-100 translate-y-0 sm:scale-100"
            leave-active-class="duration-200 ease-in"
            leave-from-class="opacity-100 translate-y-0 sm:scale-100"
            leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <div
              v-if="show"
              :class="modalClasses"
              @click.stop
            >
              <div
                v-if="!hideHeader"
                class="flex items-center justify-between p-4 border-b border-gray-200"
              >
                <h3 class="text-lg font-medium text-gray-900">
                  <slot name="title">
                    {{ title }}
                  </slot>
                </h3>
                <button
                  v-if="!hideCloseButton"
                  type="button"
                  class="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md p-1"
                  @click="handleClose"
                >
                  <svg
                    class="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>
              </div>
              
              <div class="p-4">
                <slot />
              </div>
              
              <div
                v-if="!hideFooter"
                class="flex items-center justify-end space-x-3 p-4 border-t border-gray-200"
              >
                <slot name="footer">
                  <BaseButton
                    v-if="!hideCancelButton"
                    variant="outline"
                    @click="handleCancel"
                  >
                    {{ cancelText }}
                  </BaseButton>
                  <BaseButton
                    v-if="!hideConfirmButton"
                    :loading="loading"
                    @click="handleConfirm"
                  >
                    {{ confirmText }}
                  </BaseButton>
                </slot>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import BaseButton from './BaseButton.vue'

interface Props {
  show: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  hideHeader?: boolean
  hideFooter?: boolean
  hideCloseButton?: boolean
  hideCancelButton?: boolean
  hideConfirmButton?: boolean
  cancelText?: string
  confirmText?: string
  loading?: boolean
  closeOnBackdrop?: boolean
  closeOnEscape?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  hideHeader: false,
  hideFooter: false,
  hideCloseButton: false,
  hideCancelButton: false,
  hideConfirmButton: false,
  cancelText: 'Cancel',
  confirmText: 'Confirm',
  loading: false,
  closeOnBackdrop: true,
  closeOnEscape: true,
})

const emit = defineEmits<{
  close: []
  cancel: []
  confirm: []
}>()

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-full mx-4',
}

const modalClasses = computed(() => {
  return [
    'relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all',
    'w-full',
    sizeClasses[props.size],
  ].join(' ')
})

const handleClose = () => {
  emit('close')
}

const handleCancel = () => {
  emit('cancel')
}

const handleConfirm = () => {
  emit('confirm')
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    handleClose()
  }
}

const handleEscapeKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.closeOnEscape && props.show) {
    handleClose()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey)
})
</script>