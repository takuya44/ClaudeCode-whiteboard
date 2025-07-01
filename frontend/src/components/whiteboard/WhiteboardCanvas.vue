<template>
  <div class="whiteboard-canvas-container relative w-full h-full overflow-hidden">
    <!-- Canvas -->
    <canvas
      ref="canvasRef"
      :width="canvasWidth"
      :height="canvasHeight"
      class="border border-gray-300 cursor-crosshair bg-white"
      @contextmenu.prevent
    />
    
    <!-- Loading Overlay -->
    <div
      v-if="isConnecting"
      class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center"
    >
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
        <p class="text-gray-600">
          Connecting to whiteboard...
        </p>
      </div>
    </div>

    <!-- Connection Error -->
    <div
      v-if="connectionError"
      class="absolute top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded max-w-sm"
    >
      <div class="flex">
        <div class="flex-shrink-0">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium">
            Connection Error
          </h3>
          <p class="text-sm mt-1">
            {{ connectionError }}
          </p>
          <button
            class="mt-2 text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
            @click="reconnect"
          >
            Retry Connection
          </button>
        </div>
      </div>
    </div>

    <!-- Online Users -->
    <div
      v-if="onlineUsers.length > 0"
      class="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3 border border-gray-200"
    >
      <h4 class="text-sm font-medium text-gray-700 mb-2">
        Online Users ({{ onlineUsers.length }})
      </h4>
      <div class="flex -space-x-2">
        <div
          v-for="user in onlineUsers.slice(0, 5)"
          :key="user.id"
          class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-medium border-2 border-white"
          :title="user.name"
        >
          {{ user.name.charAt(0).toUpperCase() }}
        </div>
        <div
          v-if="onlineUsers.length > 5"
          class="w-8 h-8 rounded-full bg-gray-500 flex items-center justify-center text-white text-xs font-medium border-2 border-white"
          :title="`+${onlineUsers.length - 5} more`"
        >
          +{{ onlineUsers.length - 5 }}
        </div>
      </div>
    </div>

    <!-- Cursors -->
    <div
      v-for="cursor in remoteCursors"
      :key="cursor.userId"
      :style="{
        position: 'absolute',
        left: cursor.x + 'px',
        top: cursor.y + 'px',
        transform: 'translate(-50%, -50%)',
        pointerEvents: 'none',
        zIndex: 1000
      }"
      class="flex items-center"
    >
      <div class="w-3 h-3 bg-red-500 rounded-full shadow-lg" />
      <div class="ml-2 bg-red-500 text-white text-xs px-2 py-1 rounded shadow-lg whitespace-nowrap">
        {{ cursor.userName }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useCanvas } from '@/composables/useCanvas'
import { useWebSocket } from '@/composables/useWebSocket'
import type { DrawingElement, DrawingTool, User } from '@/types'

interface Props {
  whiteboardId: string
  tool: DrawingTool
  width?: number
  height?: number
}

interface Emits {
  (e: 'drawing-updated', elements: DrawingElement[]): void
  (e: 'users-changed', users: User[]): void
}

const props = withDefaults(defineProps<Props>(), {
  width: 1200,
  height: 800
})

const emit = defineEmits<Emits>()

// Template refs
const canvasRef = ref<HTMLCanvasElement | null>(null)

// Canvas dimensions
const canvasWidth = ref(props.width)
const canvasHeight = ref(props.height)

// Canvas composable
const {
  canvasState,
  setupCanvas,
  cleanupCanvas,
  redrawCanvas,
  clearCanvas,
  undo,
  redo,
  setTool,
  loadElements,
  onDrawingEvent,
  canUndo,
  canRedo
} = useCanvas(canvasRef)

// WebSocket composable
const webSocket = useWebSocket()

// State
const isConnecting = ref(false)
const connectionError = ref<string | null>(null)
const onlineUsers = ref<User[]>([])
const remoteCursors = ref<Array<{
  userId: string
  userName: string
  x: number
  y: number
}>>([])

// Current user (should come from auth store in real app)
const currentUser = reactive({
  id: 'user-' + Math.random().toString(36).substr(2, 9),
  name: 'User ' + Math.random().toString(36).substr(2, 3)
})

// Icons
const ExclamationTriangleIcon = () => 'warning'

// Methods
const initializeCanvas = async () => {
  await nextTick()
  
  if (!canvasRef.value) {
    console.error('Canvas ref not available')
    return
  }

  // Setup canvas drawing
  setupCanvas()
  
  // Set initial tool
  setTool(props.tool)
  
  // Setup drawing event listener
  onDrawingEvent((event) => {
    if (event.type === 'end' && event.element) {
      // Send drawing update via WebSocket
      webSocket.sendDrawingUpdate(event.element, currentUser.id)
      
      // Emit local event
      emit('drawing-updated', canvasState.elements)
    }
  })
}

const connectToWebSocket = async () => {
  try {
    isConnecting.value = true
    connectionError.value = null
    
    await webSocket.connect(props.whiteboardId, currentUser.id)
    
    // Set up message handlers
    setupWebSocketHandlers()
    
    // Send user join message
    webSocket.sendUserJoin(currentUser.id, currentUser.name)
    
  } catch (error) {
    connectionError.value = error instanceof Error ? error.message : 'Connection failed'
  } finally {
    isConnecting.value = false
  }
}

const setupWebSocketHandlers = () => {
  // Handle drawing updates from other users
  webSocket.onMessage('draw', (data) => {
    if (data.element && data.element.userId !== currentUser.id) {
      canvasState.elements.push(data.element)
      redrawCanvas()
      emit('drawing-updated', canvasState.elements)
    }
  })

  // Handle user join
  webSocket.onMessage('user_join', (data) => {
    if (data.userId !== currentUser.id) {
      const existingUser = onlineUsers.value.find(u => u.id === data.userId)
      if (!existingUser) {
        onlineUsers.value.push({
          id: data.userId,
          name: data.userName,
          email: '',
          role: 'user',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
        emit('users-changed', onlineUsers.value)
      }
    }
  })

  // Handle user leave
  webSocket.onMessage('user_leave', (data) => {
    const index = onlineUsers.value.findIndex(u => u.id === data.userId)
    if (index > -1) {
      onlineUsers.value.splice(index, 1)
      emit('users-changed', onlineUsers.value)
    }
    
    // Remove cursor
    const cursorIndex = remoteCursors.value.findIndex(c => c.userId === data.userId)
    if (cursorIndex > -1) {
      remoteCursors.value.splice(cursorIndex, 1)
    }
  })

  // Handle cursor updates
  webSocket.onMessage('cursor', (data) => {
    if (data.userId !== currentUser.id) {
      const existingCursor = remoteCursors.value.find(c => c.userId === data.userId)
      if (existingCursor) {
        existingCursor.x = data.x
        existingCursor.y = data.y
      } else {
        const user = onlineUsers.value.find(u => u.id === data.userId)
        if (user) {
          remoteCursors.value.push({
            userId: data.userId,
            userName: user.name,
            x: data.x,
            y: data.y
          })
        }
      }
    }
  })
}

const reconnect = () => {
  connectToWebSocket()
}

const handleUndo = () => {
  undo()
  emit('drawing-updated', canvasState.elements)
}

const handleRedo = () => {
  redo()
  emit('drawing-updated', canvasState.elements)
}

const handleClear = () => {
  clearCanvas()
  emit('drawing-updated', canvasState.elements)
  
  // Notify other users via WebSocket
  webSocket.sendMessage({
    type: 'erase',
    data: { action: 'clear' },
    userId: currentUser.id,
    timestamp: new Date().toISOString()
  })
}

// Cursor tracking
let cursorThrottle: ReturnType<typeof setTimeout> | null = null
const handleMouseMove = (e: MouseEvent) => {
  if (cursorThrottle) return
  
  cursorThrottle = setTimeout(() => {
    const rect = canvasRef.value?.getBoundingClientRect()
    if (rect && webSocket.isConnected()) {
      webSocket.sendCursorUpdate(
        e.clientX - rect.left,
        e.clientY - rect.top,
        currentUser.id
      )
    }
    cursorThrottle = null
  }, 50) // Throttle to 20 FPS
}

const setupCursorTracking = () => {
  if (canvasRef.value) {
    canvasRef.value.addEventListener('mousemove', handleMouseMove)
  }
}

const cleanupCursorTracking = () => {
  if (canvasRef.value) {
    canvasRef.value.removeEventListener('mousemove', handleMouseMove)
  }
  if (cursorThrottle) {
    clearTimeout(cursorThrottle)
  }
}

// Watch for tool changes
watch(() => props.tool, (newTool) => {
  setTool(newTool)
}, { deep: true })

// Lifecycle
onMounted(async () => {
  await initializeCanvas()
  await connectToWebSocket()
  setupCursorTracking()
})

onUnmounted(() => {
  cleanupCanvas()
  cleanupCursorTracking()
  webSocket.disconnect()
})

// Expose methods for parent component
defineExpose({
  undo: handleUndo,
  redo: handleRedo,
  clear: handleClear,
  canUndo,
  canRedo,
  loadElements
})
</script>

<style scoped>
.whiteboard-canvas-container {
  background: radial-gradient(circle, #f0f0f0 1px, transparent 1px);
  background-size: 20px 20px;
}
</style>