import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import type { Whiteboard, DrawingElement } from '@/types'
import { whiteboardApi } from '@/api/whiteboard'
import { useWebSocket } from '@/composables/useWebSocket'
import { useAuthStore } from '@/stores/auth'

export const useWhiteboardStore = defineStore('whiteboard', () => {
  const whiteboards = ref<Whiteboard[]>([])
  const currentWhiteboard = ref<Whiteboard | null>(null)
  const drawingElements = ref<DrawingElement[]>([])
  const isLoading = ref(false)
  const selectedTool = ref<'pen' | 'rectangle' | 'circle' | 'text' | 'sticky' | 'eraser'>('pen')
  const selectedColor = ref('#000000')
  const strokeWidth = ref(2)

  // WebSocket integration
  const authStore = useAuthStore()
  const webSocket = useWebSocket()
  
  // Track WebSocket connection state
  const isWebSocketConnected = ref(false)

  const currentWhiteboardElements = computed(() => {
    if (!currentWhiteboard.value) return []
    return drawingElements.value.filter(el => el.whiteboardId === currentWhiteboard.value!.id)
  })

  const fetchWhiteboards = async (page = 1, perPage = 10) => {
    isLoading.value = true
    try {
      const response = await whiteboardApi.getWhiteboards(page, perPage)
      
      if (response.success && response.data) {
        // Backend returns array directly, not paginated response
        const whiteboardsData = Array.isArray(response.data) ? response.data : (response.data.data || [])
        
        // If it's the first page, replace the entire array
        if (page === 1) {
          whiteboards.value = whiteboardsData
        } else {
          // If it's a subsequent page, append to the existing array
          whiteboards.value.push(...whiteboardsData)
        }
        
        // Return compatible format
        return {
          data: whiteboardsData,
          total: whiteboardsData.length,
          page,
          perPage
        }
      } else {
        // Handle case where response is not successful
        console.warn('API request failed:', response.message)
        if (page === 1) {
          whiteboards.value = []
        }
        return { data: [], total: 0, page, perPage }
      }
    } catch (error) {
      console.error('Fetch whiteboards error:', error)
      // Ensure whiteboards is always an array even on error
      if (page === 1) {
        whiteboards.value = []
      }
      // Don't throw error, return empty result instead
      return { data: [], total: 0, page, perPage }
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

  const setCurrentWhiteboard = async (whiteboard: Whiteboard | null) => {
    // Disconnect from previous whiteboard if connected
    if (isWebSocketConnected.value) {
      webSocket.disconnect()
      isWebSocketConnected.value = false
    }

    currentWhiteboard.value = whiteboard
    if (whiteboard) {
      // Load drawing elements for this whiteboard
      await loadDrawingElements(whiteboard.id)
      
      // Connect to WebSocket for real-time collaboration
      if (authStore.user) {
        try {
          await webSocket.connect(whiteboard.id, authStore.user.id)
          isWebSocketConnected.value = true
          
          // Setup WebSocket message handlers for this whiteboard
          setupWebSocketHandlers()
          
          // Send user join notification
          webSocket.sendUserJoin(authStore.user.id, authStore.user.name)
        } catch (error) {
          console.error('Failed to connect to WebSocket:', error)
        }
      }
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
    
    // Send to WebSocket for real-time sync
    if (isWebSocketConnected.value && authStore.user) {
      webSocket.sendDrawingUpdate(newElement, authStore.user.id)
    }
    
    return newElement
  }

  const updateDrawingElement = (elementId: string, updates: Partial<DrawingElement>) => {
    const elementIndex = drawingElements.value.findIndex(el => el.id === elementId)
    if (elementIndex !== -1) {
      const updatedElement = {
        ...drawingElements.value[elementIndex],
        ...updates,
        updatedAt: new Date().toISOString(),
      }
      
      drawingElements.value[elementIndex] = updatedElement
      
      // Send to WebSocket for real-time sync
      if (isWebSocketConnected.value && authStore.user) {
        webSocket.sendDrawingUpdate(updatedElement, authStore.user.id)
      }
    }
  }

  const removeDrawingElement = (elementId: string) => {
    const elementIndex = drawingElements.value.findIndex(el => el.id === elementId)
    if (elementIndex !== -1) {
      const removedElement = drawingElements.value[elementIndex]
      drawingElements.value.splice(elementIndex, 1)
      
      // Send to WebSocket for real-time sync
      if (isWebSocketConnected.value && authStore.user) {
        webSocket.sendMessage({
          type: 'erase',
          data: { elementId, element: removedElement },
          userId: authStore.user.id,
          timestamp: new Date().toISOString()
        })
      }
    }
  }

  const clearWhiteboard = () => {
    if (!currentWhiteboard.value) return
    
    const whiteboardId = currentWhiteboard.value.id
    const elementsToRemove = drawingElements.value.filter(
      el => el.whiteboardId === whiteboardId
    )
    
    drawingElements.value = drawingElements.value.filter(
      el => el.whiteboardId !== whiteboardId
    )
    
    // Send to WebSocket for real-time sync
    if (isWebSocketConnected.value && authStore.user) {
      webSocket.sendMessage({
        type: 'clear',
        data: { whiteboardId, elementsRemoved: elementsToRemove },
        userId: authStore.user.id,
        timestamp: new Date().toISOString()
      })
    }
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

  const updateWhiteboard = async (whiteboardId: string, updates: { title?: string; description?: string; isPublic?: boolean }) => {
    isLoading.value = true
    try {
      const response = await whiteboardApi.updateWhiteboard(whiteboardId, updates)
      
      if (response.success && response.data) {
        // Update the whiteboard in the list
        const index = whiteboards.value.findIndex(wb => wb.id === whiteboardId)
        if (index !== -1) {
          whiteboards.value[index] = response.data
        }
        
        // Update current whiteboard if it's the one being updated
        if (currentWhiteboard.value?.id === whiteboardId) {
          currentWhiteboard.value = response.data
        }
        
        return response.data
      } else {
        throw new Error(response.message || 'Failed to update whiteboard')
      }
    } catch (error) {
      console.error('Update whiteboard error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const deleteWhiteboard = async (whiteboardId: string) => {
    isLoading.value = true
    try {
      const response = await whiteboardApi.deleteWhiteboard(whiteboardId)
      
      if (response.success) {
        // Remove the whiteboard from the list
        const index = whiteboards.value.findIndex(wb => wb.id === whiteboardId)
        if (index !== -1) {
          whiteboards.value.splice(index, 1)
        }
        
        // If it's the current whiteboard, clear it
        if (currentWhiteboard.value?.id === whiteboardId) {
          currentWhiteboard.value = null
          drawingElements.value = drawingElements.value.filter(
            el => el.whiteboardId !== whiteboardId
          )
        }
        
        return response
      } else {
        throw new Error(response.message || 'Failed to delete whiteboard')
      }
    } catch (error) {
      console.error('Delete whiteboard error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // WebSocket message handlers
  const setupWebSocketHandlers = () => {
    // Handle incoming drawing updates
    webSocket.onMessage('draw', (data: { element: DrawingElement }) => {
      const { element } = data
      
      // Only add if it's not from the current user and element doesn't exist
      if (element.userId !== authStore.user?.id) {
        const existingIndex = drawingElements.value.findIndex(el => el.id === element.id)
        
        if (existingIndex === -1) {
          // Add new element
          drawingElements.value.push(element)
        } else {
          // Update existing element
          drawingElements.value[existingIndex] = element
        }
      }
    })

    // Handle element removal
    webSocket.onMessage('erase', (data: { elementId: string; element: DrawingElement }) => {
      const { elementId } = data
      
      // Only remove if it's not from the current user
      if (data.element?.userId !== authStore.user?.id) {
        const elementIndex = drawingElements.value.findIndex(el => el.id === elementId)
        if (elementIndex !== -1) {
          drawingElements.value.splice(elementIndex, 1)
        }
      }
    })

    // Handle whiteboard clear
    webSocket.onMessage('clear', (data: { whiteboardId: string; elementsRemoved: DrawingElement[] }) => {
      const { whiteboardId } = data
      
      // Clear elements for this whiteboard (if it's the current one)
      if (currentWhiteboard.value?.id === whiteboardId) {
        drawingElements.value = drawingElements.value.filter(
          el => el.whiteboardId !== whiteboardId
        )
      }
    })

    // Handle user presence
    webSocket.onMessage('user_join', (data: { userId: string; userName: string }) => {
      console.log(`User ${data.userName} joined the whiteboard`)
      // TODO: Update online users list
    })

    webSocket.onMessage('user_leave', (data: { userId: string }) => {
      console.log(`User ${data.userId} left the whiteboard`)
      // TODO: Update online users list
    })

    // Handle cursor updates
    webSocket.onMessage('cursor', (data: { x: number; y: number; userId: string }) => {
      // TODO: Update other users' cursor positions
      console.log(`User ${data.userId} cursor at:`, data.x, data.y)
    })

    // Handle pong response
    webSocket.onMessage('pong', () => {
      // WebSocket heartbeat response - connection is alive
    })
  }

  // Disconnect WebSocket when leaving whiteboard
  const disconnectWebSocket = () => {
    if (isWebSocketConnected.value && authStore.user) {
      webSocket.sendUserLeave(authStore.user.id)
      webSocket.disconnect()
      isWebSocketConnected.value = false
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
    isWebSocketConnected: readonly(isWebSocketConnected),
    fetchWhiteboards,
    createWhiteboard,
    updateWhiteboard,
    deleteWhiteboard,
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
    disconnectWebSocket,
    webSocket,
  }
})