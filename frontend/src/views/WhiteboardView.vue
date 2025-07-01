<template>
  <div class="h-screen flex flex-col bg-white">
    <!-- Header -->
    <div class="border-b border-gray-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <BaseButton
            variant="outline"
            size="sm"
            @click="$router.push('/dashboard')"
          >
            <template #icon-left>
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </template>
            Back to Dashboard
          </BaseButton>
          
          <div>
            <h1 class="text-lg font-semibold text-gray-900">
              {{ currentWhiteboard?.title || 'Loading...' }}
            </h1>
            <p
              v-if="currentWhiteboard?.description"
              class="text-sm text-gray-500"
            >
              {{ currentWhiteboard.description }}
            </p>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <BaseButton
            variant="outline"
            size="sm"
          >
            Share
          </BaseButton>
          <BaseButton
            variant="outline"
            size="sm"
          >
            Export
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="border-b border-gray-200 px-4 py-2">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <!-- Drawing Tools -->
          <div class="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              v-for="tool in drawingTools"
              :key="tool.id"
              :class="[
                'px-3 py-2 rounded-md text-sm font-medium transition-colors',
                selectedTool === tool.id
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              ]"
              @click="setSelectedTool(tool.id)"
            >
              {{ tool.name }}
            </button>
          </div>
          
          <!-- Color Picker -->
          <div class="flex items-center space-x-2 ml-4">
            <input
              :value="selectedColor"
              type="color"
              class="w-8 h-8 rounded border border-gray-300"
              @change="handleColorChange"
            >
            <span class="text-sm text-gray-600">Color</span>
          </div>
          
          <!-- Stroke Width -->
          <div class="flex items-center space-x-2 ml-4">
            <input
              :value="strokeWidth"
              type="range"
              min="1"
              max="20"
              class="w-20"
              @input="handleStrokeWidthChange"
            >
            <span class="text-sm text-gray-600 w-8">{{ strokeWidth }}px</span>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <BaseButton
            variant="outline"
            size="sm"
            @click="clearCanvas"
          >
            Clear All
          </BaseButton>
          <BaseButton
            variant="outline"
            size="sm"
          >
            Undo
          </BaseButton>
          <BaseButton
            variant="outline"
            size="sm"
          >
            Redo
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Canvas Area -->
    <div class="flex-1 relative bg-gray-50">
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="text-center text-gray-500">
          <svg
            class="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
            />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">
            Canvas Implementation
          </h3>
          <p class="mt-1 text-sm text-gray-500">
            Canvas drawing functionality will be implemented by Frontend Developer B
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useWhiteboardStore } from '@/stores/whiteboard'
import { BaseButton } from '@/components/ui'

const route = useRoute()
const whiteboardStore = useWhiteboardStore()

const whiteboardId = route.params.id as string

const currentWhiteboard = computed(() => whiteboardStore.currentWhiteboard)
const selectedTool = computed(() => whiteboardStore.selectedTool)
const selectedColor = computed(() => whiteboardStore.selectedColor)
const strokeWidth = computed(() => whiteboardStore.strokeWidth)

const drawingTools = [
  { id: 'pen', name: 'Pen' },
  { id: 'rectangle', name: 'Rectangle' },
  { id: 'circle', name: 'Circle' },
  { id: 'text', name: 'Text' },
  { id: 'sticky', name: 'Sticky Note' },
  { id: 'eraser', name: 'Eraser' },
]

const setSelectedTool = (tool: string) => {
  whiteboardStore.setSelectedTool(tool as any)
}

const handleColorChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  whiteboardStore.setSelectedColor(target.value)
}

const handleStrokeWidthChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  whiteboardStore.setStrokeWidth(Number(target.value))
}

const clearCanvas = () => {
  if (confirm('Are you sure you want to clear the entire canvas?')) {
    whiteboardStore.clearWhiteboard()
  }
}

onMounted(async () => {
  // TODO: Load whiteboard data by ID
  console.log('Loading whiteboard:', whiteboardId)
  
  // Mock whiteboard data for now
  const mockWhiteboard = {
    id: whiteboardId,
    title: 'My Whiteboard',
    description: 'A collaborative workspace',
    ownerId: 'user1',
    isPublic: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    collaborators: []
  }
  
  whiteboardStore.setCurrentWhiteboard(mockWhiteboard)
})
</script>