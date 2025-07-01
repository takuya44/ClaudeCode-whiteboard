import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import type { Whiteboard, DrawingElement } from '@/types'

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

  const fetchWhiteboards = async () => {
    isLoading.value = true
    try {
      // TODO: API call to fetch whiteboards
      // const response = await api.get('/whiteboards')
      // whiteboards.value = response.data
      
      console.log('Fetching whiteboards')
    } catch (error) {
      console.error('Fetch whiteboards error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const createWhiteboard = async (whiteboardData: Omit<Whiteboard, 'id' | 'createdAt' | 'updatedAt'>) => {
    isLoading.value = true
    try {
      // TODO: API call to create whiteboard
      // const response = await api.post('/whiteboards', whiteboardData)
      // const newWhiteboard = response.data
      // whiteboards.value.push(newWhiteboard)
      // return newWhiteboard
      
      console.log('Creating whiteboard:', whiteboardData)
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
      // TODO: API call to load drawing elements
      // const response = await api.get(`/whiteboards/${whiteboardId}/elements`)
      // drawingElements.value = response.data
      
      console.log('Loading drawing elements for whiteboard:', whiteboardId)
    } catch (error) {
      console.error('Load drawing elements error:', error)
      throw error
    }
  }

  const addDrawingElement = (element: Omit<DrawingElement, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newElement: DrawingElement = {
      ...element,
      id: `element_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
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
  }
})