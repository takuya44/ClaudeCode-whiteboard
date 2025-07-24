<template>
  <BaseModal
    :show="show"
    title="Edit Whiteboard"
    size="lg"
    :loading="isLoading"
    confirm-text="Save"
    cancel-text="Cancel"
    @close="handleClose"
    @cancel="handleClose"
    @confirm="handleSave"
  >
    <form
      class="space-y-4"
      @submit.prevent="handleSave"
    >
      <BaseInput
        v-model="formData.title"
        label="Title"
        placeholder="Enter whiteboard title"
        :error="errors.title"
        required
      />
      
      <div class="space-y-1">
        <label class="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          v-model="formData.description"
          rows="3"
          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
          placeholder="Enter whiteboard description (optional)"
        />
      </div>
      
      <div class="flex items-center space-x-2">
        <input
          id="isPublic"
          v-model="formData.isPublic"
          type="checkbox"
          class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        >
        <label
          for="isPublic"
          class="text-sm text-gray-700"
        >
          Make this whiteboard public
        </label>
      </div>
      
      <div
        v-if="formData.isPublic"
        class="bg-blue-50 border border-blue-200 rounded-md p-3"
      >
        <p class="text-sm text-blue-800">
          Public whiteboards can be viewed by anyone with the link.
        </p>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useWhiteboardStore } from '@/stores/whiteboard'
import { useToast } from '@/composables/useToast'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import type { Whiteboard } from '@/types'

interface Props {
  show: boolean
  whiteboard: Whiteboard | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  saved: [whiteboard: Whiteboard]
}>()

const whiteboardStore = useWhiteboardStore()
const { showError } = useToast()

const isLoading = ref(false)
const formData = reactive({
  title: '',
  description: '',
  isPublic: false,
})

const errors = reactive({
  title: '',
})

// Watch for whiteboard changes to populate form
watch(() => props.whiteboard, (newWhiteboard) => {
  if (newWhiteboard) {
    formData.title = newWhiteboard.title
    formData.description = newWhiteboard.description || ''
    formData.isPublic = newWhiteboard.isPublic
  }
}, { immediate: true })

const validateForm = () => {
  errors.title = ''
  
  if (!formData.title.trim()) {
    errors.title = 'Title is required'
    return false
  }
  
  if (formData.title.length > 100) {
    errors.title = 'Title must be less than 100 characters'
    return false
  }
  
  return true
}

const handleSave = async () => {
  if (!validateForm() || !props.whiteboard) {
    return
  }
  
  isLoading.value = true
  
  try {
    const updatedWhiteboard = await whiteboardStore.updateWhiteboard(props.whiteboard.id, {
      title: formData.title.trim(),
      description: formData.description.trim() || undefined,
      isPublic: formData.isPublic,
    })
    
    emit('saved', updatedWhiteboard)
    emit('close')
  } catch (error) {
    console.error('Failed to update whiteboard:', error)
    showError('Failed to update whiteboard. Please try again.')
  } finally {
    isLoading.value = false
  }
}

const handleClose = () => {
  // Reset form and errors
  errors.title = ''
  emit('close')
}
</script>