import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import type { Whiteboard, DrawingElement } from '@/types'
import { whiteboardApi } from '@/api/whiteboard'

export const useWhiteboardStore = defineStore('whiteboard', () => {
  const whiteboards = ref<Whiteboard[]>([])
  const currentWhiteboard = ref<Whiteboard | null>(null)
  const drawingElements = ref<DrawingElement[]>([])
  const isLoading = ref(false)
  const selectedTool = ref<'pen' | 'rectangle' | 'circle' | 'text' | 'sticky' | 'eraser'>('pen')
  const selectedColor = ref('#000000')
  const strokeWidth = ref(2)

  const currentWhiteboardElements = computed(() => {
    if (!currentWhiteboard.value) return []
    return drawingElements.value.filter(el => el.whiteboardId === currentWhiteboard.value!.id)
  })

  const fetchWhiteboards = async (page = 1, perPage = 10) => {
    isLoading.value = true
    try {
      const response = await whiteboardApi.getWhiteboards(page, perPage)
      
      if (response.success && response.data) {
        // If it's the first page, replace the entire array
        if (page === 1) {
          whiteboards.value = response.data.data
        } else {
          // If it's a subsequent page, append to the existing array
          whiteboards.value.push(...response.data.data)
        }
        
        return response.data
      } else {
        throw new Error(response.message || 'Failed to fetch whiteboards')
      }
    } catch (error) {
      console.error('Fetch whiteboards error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const createWhiteboard = async (whiteboardData: { title: string; description?: string; isPublic: boolean }) => {
    isLoading.value = true
    try {
      const response = await whiteboardApi.createWhiteboard(whiteboardData)
      
      if (response.success && response.data) {
        // Add the new whiteboard to the beginning of the array
        whiteboards.value.unshift(response.data)
        return response.data
      } else {
        throw new Error(response.message || 'Failed to create whiteboard')
      }
    } catch (error) {
      console.error('Create whiteboard error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const setCurrentWhiteboard = (whiteboard: Whiteboard | null) => {
    currentWhiteboard.value = whiteboard
    if (whiteboard) {
      // TODO: Load drawing elements for this whiteboard
      loadDrawingElements(whiteboard.id)
    }
  }

  const loadDrawingElements = async (whiteboardId: string) => {
    try {
      const response = await whiteboardApi.getWhiteboardElements(whiteboardId)
      
      if (response.success && response.data) {
        // Filter out elements for this whiteboard and add the new ones
        drawingElements.value = drawingElements.value.filter(el => el.whiteboardId !== whiteboardId)
        drawingElements.value.push(...response.data)
        return response.data
      } else {
        throw new Error(response.message || 'Failed to load drawing elements')
      }
    } catch (error) {
      console.error('Load drawing elements error:', error)
      throw error
    }
  }

  const addDrawingElement = (element: Omit<DrawingElement, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newElement: DrawingElement = {
      ...element,
      id: `element_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    
    drawingElements.value.push(newElement)
    
    // TODO: Send to WebSocket for real-time sync
    console.log('Adding drawing element:', newElement)
    
    return newElement
  }

  const updateDrawingElement = (elementId: string, updates: Partial<DrawingElement>) => {
    const elementIndex = drawingElements.value.findIndex(el => el.id === elementId)
    if (elementIndex !== -1) {
      drawingElements.value[elementIndex] = {
        ...drawingElements.value[elementIndex],
        ...updates,
        updatedAt: new Date().toISOString(),
      }
      
      // TODO: Send to WebSocket for real-time sync
      console.log('Updating drawing element:', elementId, updates)
    }
  }

  const removeDrawingElement = (elementId: string) => {
    const elementIndex = drawingElements.value.findIndex(el => el.id === elementId)
    if (elementIndex !== -1) {
      drawingElements.value.splice(elementIndex, 1)
      
      // TODO: Send to WebSocket for real-time sync
      console.log('Removing drawing element:', elementId)
    }
  }

  const clearWhiteboard = () => {
    if (!currentWhiteboard.value) return
    
    drawingElements.value = drawingElements.value.filter(
      el => el.whiteboardId !== currentWhiteboard.value!.id
    )
    
    // TODO: Send to WebSocket for real-time sync
    console.log('Clearing whiteboard:', currentWhiteboard.value.id)
  }

  const setSelectedTool = (tool: typeof selectedTool.value) => {
    selectedTool.value = tool
  }

  const setSelectedColor = (color: string) => {
    selectedColor.value = color
  }

  const setStrokeWidth = (width: number) => {
    strokeWidth.value = width
  }

  const shareWhiteboard = async (whiteboardId: string, userEmails: string[]) => {
    try {
      const response = await whiteboardApi.shareWhiteboard(whiteboardId, userEmails)
      
      if (response.success) {
        // 共有成功時にホワイトボード一覧を更新
        await fetchWhiteboards()
        return response
      } else {
        throw new Error(response.message || 'Failed to share whiteboard')
      }
    } catch (error) {
      console.error('Share whiteboard error:', error)
      throw error
    }
  }

  const getCollaborators = async (whiteboardId: string) => {
    try {
      const response = await whiteboardApi.getCollaborators(whiteboardId)
      
      if (response.success && response.data) {
        return response.data
      } else {
        throw new Error(response.message || 'Failed to get collaborators')
      }
    } catch (error) {
      console.error('Get collaborators error:', error)
      throw error
    }
  }

  const removeCollaborator = async (whiteboardId: string, userId: string) => {
    try {
      const response = await whiteboardApi.removeCollaborator(whiteboardId, userId)
      
      if (response.success) {
        // 削除成功時にホワイトボード一覧を更新
        await fetchWhiteboards()
        return response
      } else {
        throw new Error(response.message || 'Failed to remove collaborator')
      }
    } catch (error) {
      console.error('Remove collaborator error:', error)
      throw error
    }
  }

  return {
    whiteboards: readonly(whiteboards),
    currentWhiteboard: readonly(currentWhiteboard),
    drawingElements: readonly(drawingElements),
    currentWhiteboardElements,
    isLoading: readonly(isLoading),
    selectedTool: readonly(selectedTool),
    selectedColor: readonly(selectedColor),
    strokeWidth: readonly(strokeWidth),
    fetchWhiteboards,
    createWhiteboard,
    setCurrentWhiteboard,
    loadDrawingElements,
    addDrawingElement,
    updateDrawingElement,
    removeDrawingElement,
    clearWhiteboard,
    setSelectedTool,
    setSelectedColor,
    setStrokeWidth,
    shareWhiteboard,
    getCollaborators,
    removeCollaborator,
  }
})