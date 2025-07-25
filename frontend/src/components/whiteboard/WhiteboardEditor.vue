<template>
  <div class="whiteboard-editor flex h-full">
    <!-- Sidebar with toolbar -->
    <div class="sidebar flex-shrink-0 w-80 bg-gray-50 border-r border-gray-200 p-4">
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-2">
          {{ whiteboard?.title || 'Whiteboard' }}
        </h2>
        <p class="text-sm text-gray-600">
          {{ whiteboard?.description || 'Collaborative whiteboard' }}
        </p>
      </div>

      <!-- Drawing Toolbar -->
      <DrawingToolbar
        v-model:tool="currentTool"
        :can-undo="canUndo"
        :can-redo="canRedo"
        @undo="handleUndo"
        @redo="handleRedo"
        @clear="handleClear"
      />

      <!-- Whiteboard Info -->
      <div class="mt-6 p-4 bg-white rounded-lg border border-gray-200">
        <h3 class="text-sm font-medium text-gray-900 mb-3">
          Whiteboard Info
        </h3>
        
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Elements:</span>
            <span class="font-medium">{{ elementCount }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600">Online Users:</span>
            <span class="font-medium">{{ onlineUserCount }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600">Connection:</span>
            <span
              :class="[
                'font-medium',
                isConnected ? 'text-green-600' : 'text-red-600'
              ]"
            >
              {{ isConnected ? 'Connected' : 'Disconnected' }}
            </span>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-gray-200">
          <button
            :disabled="isSaving"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            @click="saveWhiteboard"
          >
            <span
              v-if="isSaving"
              class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"
            />
            {{ isSaving ? 'Saving...' : 'Save Whiteboard' }}
          </button>
        </div>
      </div>

      <!-- Keyboard Shortcuts -->
      <div class="mt-6 p-4 bg-white rounded-lg border border-gray-200">
        <h3 class="text-sm font-medium text-gray-900 mb-3">
          Keyboard Shortcuts
        </h3>
        <div class="space-y-1 text-xs text-gray-600">
          <div class="flex justify-between">
            <span>Undo</span>
            <kbd class="bg-gray-100 px-2 py-1 rounded">Ctrl+Z</kbd>
          </div>
          <div class="flex justify-between">
            <span>Redo</span>
            <kbd class="bg-gray-100 px-2 py-1 rounded">Ctrl+Y</kbd>
          </div>
          <div class="flex justify-between">
            <span>Clear</span>
            <kbd class="bg-gray-100 px-2 py-1 rounded">Ctrl+D</kbd>
          </div>
          <div class="flex justify-between">
            <span>Save</span>
            <kbd class="bg-gray-100 px-2 py-1 rounded">Ctrl+S</kbd>
          </div>
        </div>
      </div>
    </div>

    <!-- Main canvas area -->
    <div class="canvas-area flex-1 flex flex-col">
      <!-- Top bar -->
      <div class="top-bar flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200">
        <div class="flex items-center space-x-4">
          <h1 class="text-xl font-semibold text-gray-900">
            {{ whiteboard?.title || 'Untitled Whiteboard' }}
          </h1>
          
          <div class="flex items-center space-x-2">
            <div
              class="w-2 h-2 rounded-full"
              :class="[
                isConnected ? 'bg-green-500' : 'bg-red-500'
              ]"
            />
            <span class="text-sm text-gray-600">
              {{ isConnected ? 'Connected' : 'Disconnected' }}
            </span>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <!-- Edit button -->
          <button
            v-if="canEdit"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            @click="showEditModal = true"
          >
            <svg 
              class="w-4 h-4 mr-2 inline" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path 
                d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" 
              />
            </svg>
            Edit
          </button>

          <!-- Collaborators button -->
          <button
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            @click="handleManageCollaborators"
          >
            <svg 
              class="w-4 h-4 mr-2 inline" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path 
                d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" 
              />
            </svg>
            メンバー
          </button>

          <!-- Share button -->
          <button
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            @click="handleShare"
          >
            <svg 
              class="w-4 h-4 mr-2 inline" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path 
                d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" 
              />
            </svg>
            共有
          </button>

          <!-- Delete button -->
          <button
            v-if="isOwner"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            @click="showDeleteDialog = true"
          >
            <svg
              class="w-4 h-4 mr-2 inline"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                clip-rule="evenodd"
              />
            </svg>
            削除
          </button>

          <!-- Zoom controls -->
          <div class="flex items-center space-x-2">
            <button
              class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
              title="Zoom Out"
              @click="zoomOut"
            >
              <ZoomOutIcon class="w-5 h-5" />
            </button>
            
            <span class="text-sm text-gray-600 min-w-[60px] text-center">
              {{ Math.round(zoomLevel * 100) }}%
            </span>
            
            <button
              class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
              title="Zoom In"
              @click="zoomIn"
            >
              <ZoomInIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- View controls -->
          <button
            class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
            title="Reset View"
            @click="resetView"
          >
            <ArrowsPointingOutIcon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Canvas container -->
      <div class="canvas-container flex-1 overflow-hidden relative">
        <!-- Loading indicator -->
        <div
          v-if="isLoading"
          class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10"
        >
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />
            <p class="mt-2 text-gray-600">
              Loading whiteboard...
            </p>
          </div>
        </div>
        
        <div
          class="canvas-wrapper absolute inset-0"
          :style="{
            transform: `scale(${zoomLevel}) translate(${panX}px, ${panY}px)`,
            transformOrigin: 'top left'
          }"
        >
          <WhiteboardCanvas
            ref="canvasRef"
            :whiteboard-id="whiteboardId"
            :tool="currentTool"
            :width="canvasWidth"
            :height="canvasHeight"
            @drawing-updated="handleDrawingUpdated"
            @users-changed="handleUsersChanged"
          />
        </div>
      </div>
    </div>

    <!-- Share Dialog -->
    <WhiteboardShareDialog
      :show="showShareDialog"
      :whiteboard="whiteboard"
      @close="showShareDialog = false"
      @shared="handleShared"
    />

    <!-- Collaborator Management Dialog -->
    <CollaboratorManagementDialog
      :show="showCollaboratorDialog"
      :whiteboard="whiteboard"
      @close="showCollaboratorDialog = false"
      @open-share="handleOpenShareFromCollaborator"
      @collaborator-removed="handleCollaboratorRemoved"
    />

    <!-- Edit Modal -->
    <WhiteboardEditModal
      :show="showEditModal"
      :whiteboard="whiteboard"
      @close="showEditModal = false"
      @saved="handleWhiteboardUpdated"
    />

    <!-- Delete Dialog -->
    <WhiteboardDeleteDialog
      :show="showDeleteDialog"
      :whiteboard-id="whiteboardId"
      :whiteboard-title="whiteboard?.title || 'Untitled Whiteboard'"
      :collaborator-count="whiteboard?.collaborators?.length || 0"
      @close="showDeleteDialog = false"
      @deleted="handleDeleteWhiteboard"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DrawingToolbar from './DrawingToolbar.vue'
import WhiteboardCanvas from './WhiteboardCanvas.vue'
import WhiteboardShareDialog from './WhiteboardShareDialog.vue'
import CollaboratorManagementDialog from './CollaboratorManagementDialog.vue'
import WhiteboardEditModal from './WhiteboardEditModal.vue'
import WhiteboardDeleteDialog from './WhiteboardDeleteDialog.vue'
import { whiteboardApi, validateAndFixElement } from '@/api/whiteboard'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { useWhiteboardStore } from '@/stores/whiteboard'
import type { DrawingTool, DrawingElement, Whiteboard, User } from '@/types'

interface Props {
  whiteboardId?: string
}

const props = defineProps<Props>()
const route = useRoute()
const router = useRouter()
const { showError, showSuccess } = useToast()

// Refs
const canvasRef = ref<InstanceType<typeof WhiteboardCanvas> | null>(null)

// State
const whiteboardId = ref(props.whiteboardId || route.params.id as string)
const whiteboard = ref<Whiteboard | null>(null)
const currentTool = ref<DrawingTool>({
  type: 'pen',
  color: '#000000',
  strokeWidth: 2,
  fill: '#ffffff'  // デフォルトを白色に設定
})

const elementCount = ref(0)
const onlineUserCount = ref(0)
const isConnected = ref(false)
const isSaving = ref(false)
const isLoading = ref(false)
const showShareDialog = ref(false)
const showCollaboratorDialog = ref(false)
const showEditModal = ref(false)
const showDeleteDialog = ref(false)

// Canvas settings
const canvasWidth = ref(1200)
const canvasHeight = ref(800)

// View controls
const zoomLevel = ref(1)
const panX = ref(0)
const panY = ref(0)
const minZoom = 0.1
const maxZoom = 5

// Icons
const ZoomInIcon = () => 'zoom-in'
const ZoomOutIcon = () => 'zoom-out'
const ArrowsPointingOutIcon = () => 'arrows-pointing-out'

// Computed
const canUndo = computed(() => canvasRef.value?.canUndo || false)
const canRedo = computed(() => canvasRef.value?.canRedo || false)
const authStore = useAuthStore()

const canEdit = computed(() => {
  if (!whiteboard.value || !authStore.user) return false

  // Check if user is the owner
  if (whiteboard.value.ownerId === authStore.user.id) return true

  // Check if user is a collaborator
  const isCollaborator = whiteboard.value.collaborators?.some(
    collaborator => collaborator.id === authStore.user?.id
  )
  
  return isCollaborator || false
})

const isOwner = computed(() => {
  return whiteboard.value && authStore.user && whiteboard.value.ownerId === authStore.user.id
})

// Methods
const loadWhiteboard = async () => {
  try {
    if (!whiteboardId.value) return
    
    isLoading.value = true
    
    // Fetch whiteboard data and elements in parallel for better performance
    const [response, elementsResponse] = await Promise.all([
      whiteboardApi.getWhiteboard(whiteboardId.value),
      whiteboardApi.getWhiteboardElements(whiteboardId.value)
    ])
    
    if (response.success && response.data) {
      console.log('Whiteboard API response:', response.data)
      whiteboard.value = response.data
      
      // Load existing elements into canvas
      if (elementsResponse.success && elementsResponse.data && canvasRef.value) {
        // Validate and fix elements loaded from backend
        const elements: DrawingElement[] = elementsResponse.data.map((element: any) => {
          return validateAndFixElement(element)
        })
        console.log('Elements loaded and validated from backend:', {
          originalCount: elementsResponse.data.length,
          validatedCount: elements.length,
          elements: elements
        })
        canvasRef.value.loadElements(elements)
        elementCount.value = elements.length
      }
    } else {
      throw new Error(response.message || 'Failed to load whiteboard')
    }
  } catch (error: unknown) {
    console.error('Failed to load whiteboard:', error)
    
    // Handle 404 error - whiteboard not found
    const axiosError = error as { response?: { status: number } }
    if (axiosError.response?.status === 404) {
      showError('Whiteboard not found')
      router.push('/app/dashboard')
    } else {
      // Handle other errors
      showError('Failed to load whiteboard. Please try again.')
    }
  } finally {
    isLoading.value = false
  }
}

const saveWhiteboard = async () => {
  if (!whiteboard.value || isSaving.value || !canvasRef.value) return
  
  try {
    isSaving.value = true
    
    // Get current canvas elements
    const currentElements = canvasRef.value.canvasState.elements
    
    console.log('Saving elements:', {
      whiteboardId: whiteboardId.value,
      elementCount: currentElements.length,
      elements: currentElements
    })
    
    // 各要素の詳細をログ出力
    currentElements.forEach((element, index) => {
      console.log(`Original Element ${index}:`, {
        id: element.id,
        type: element.type,
        x: element.x,
        y: element.y,
        color: element.color,
        colorExists: !!element.color,
        colorType: typeof element.color,
        strokeWidth: element.strokeWidth,
        fill: element.fill,
        points: element.points?.length || 0,
        fullElement: element
      })
    })
    
    // Save elements to backend
    const saveResponse = await whiteboardApi.saveElements(whiteboardId.value, currentElements)
    
    if (saveResponse.success) {
      showSuccess('Whiteboard saved successfully!')
    } else {
      throw new Error(saveResponse.message || 'Failed to save whiteboard')
    }
  } catch (error) {
    console.error('Failed to save whiteboard:', error)
    showError(
      error instanceof Error ? error.message : 'Failed to save whiteboard. Please try again.'
    )
  } finally {
    isSaving.value = false
  }
}

const handleDrawingUpdated = (elements: DrawingElement[]) => {
  elementCount.value = elements.length
  
  // Auto-save periodically (debounced)
  // This could be improved with a proper debounce mechanism
}

const handleUsersChanged = (users: User[]) => {
  onlineUserCount.value = users.length
}

const handleUndo = () => {
  canvasRef.value?.undo()
}

const handleRedo = () => {
  canvasRef.value?.redo()
}

const handleClear = () => {
  canvasRef.value?.clear()
}

// Zoom controls
const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value * 1.2, maxZoom)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value / 1.2, minZoom)
}

const resetView = () => {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
}

const handleShare = () => {
  showShareDialog.value = true
}

const handleShared = (results: any) => {
  console.log('Whiteboard shared:', results)
  // 共有成功のフィードバックを表示するなどの処理
}

const handleManageCollaborators = () => {
  showCollaboratorDialog.value = true
}

const handleOpenShareFromCollaborator = () => {
  showCollaboratorDialog.value = false
  showShareDialog.value = true
}

const handleWhiteboardUpdated = (updatedWhiteboard: Whiteboard) => {
  whiteboard.value = updatedWhiteboard
  showSuccess('Whiteboard updated successfully')
}

const handleDeleteWhiteboard = async () => {
  const whiteboardStore = useWhiteboardStore()
  
  try {
    await whiteboardStore.deleteWhiteboard(whiteboardId.value)
    showSuccess('ホワイトボードを削除しました')
    // Redirect to dashboard after successful deletion
    router.push('/app/dashboard')
  } catch (error) {
    console.error('Failed to delete whiteboard:', error)
    showError('ホワイトボードの削除に失敗しました')
  }
}

const handleCollaboratorRemoved = (collaborator: any) => {
  console.log('Collaborator removed:', collaborator)
  // コラボレーター削除後の処理（通知表示など）
}

// Keyboard shortcuts
const handleKeydown = (e: KeyboardEvent) => {
  if (e.ctrlKey || e.metaKey) {
    switch (e.key) {
      case 'z':
        e.preventDefault()
        if (e.shiftKey) {
          handleRedo()
        } else {
          handleUndo()
        }
        break
      case 'y':
        e.preventDefault()
        handleRedo()
        break
      case 'd':
        e.preventDefault()
        handleClear()
        break
      case 's':
        e.preventDefault()
        saveWhiteboard()
        break
      case '=':
      case '+':
        e.preventDefault()
        zoomIn()
        break
      case '-':
        e.preventDefault()
        zoomOut()
        break
      case '0':
        e.preventDefault()
        resetView()
        break
    }
  }
}

// Watch for tool changes
watch(currentTool, () => {
  // Tool changes will be handled by the canvas component through props
}, { deep: true })

// Lifecycle
onMounted(async () => {
  await loadWhiteboard()
  
  // Add keyboard event listeners
  document.addEventListener('keydown', handleKeydown)
  
  // Simulate connection status (should come from WebSocket)
  isConnected.value = true
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.whiteboard-editor {
  height: 100vh;
  background: #f9fafb;
}

.canvas-container {
  background: #ffffff;
  background-image: 
    linear-gradient(rgba(0,0,0,.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

kbd {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
}
</style>
