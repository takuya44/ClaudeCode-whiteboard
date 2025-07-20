import { ref, computed } from 'vue'

export interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

const toasts = ref<Toast[]>([])

export const useToast = () => {
  const activeToasts = computed(() => toasts.value)

  const showToast = (message: string, type: Toast['type'] = 'info', duration = 3000) => {
    const id = Date.now().toString()
    const toast: Toast = {
      id,
      message,
      type,
      duration
    }
    
    toasts.value.push(toast)
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
  }

  const removeToast = (id: string) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const showError = (message: string) => showToast(message, 'error', 5000)
  const showSuccess = (message: string) => showToast(message, 'success')
  const showWarning = (message: string) => showToast(message, 'warning')
  const showInfo = (message: string) => showToast(message, 'info')

  return {
    toasts: activeToasts,
    showToast,
    showError,
    showSuccess,
    showWarning,
    showInfo,
    removeToast
  }
}