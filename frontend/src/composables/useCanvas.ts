import { ref, reactive, computed, onMounted, onUnmounted, type Ref } from 'vue'
import type { DrawingElement, DrawingTool, Point, CanvasState, DrawingEvent } from '@/types'

export function useCanvas(canvasRef: Ref<HTMLCanvasElement | null>) {
  const canvasState = reactive<CanvasState>({
    isDrawing: false,
    tool: {
      type: 'pen',
      color: '#000000',
      strokeWidth: 2,
      fill: 'transparent'
    },
    elements: [],
    history: [[]],
    currentHistoryIndex: 0
  })

  const ctx = computed(() => canvasRef.value?.getContext('2d'))
  const currentElement = ref<DrawingElement | null>(null)

  const generateId = () => Math.random().toString(36).substr(2, 9)

  const getMousePos = (e: MouseEvent): Point => {
    const rect = canvasRef.value?.getBoundingClientRect()
    if (!rect) return { x: 0, y: 0 }
    
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    }
  }

  const getTouchPos = (e: TouchEvent): Point => {
    const rect = canvasRef.value?.getBoundingClientRect()
    if (!rect || !e.touches[0]) return { x: 0, y: 0 }
    
    return {
      x: e.touches[0].clientX - rect.left,
      y: e.touches[0].clientY - rect.top
    }
  }

  const startDrawing = (point: Point) => {
    if (!ctx.value) return

    canvasState.isDrawing = true
    
    const baseElement: Partial<DrawingElement> = {
      id: generateId(),
      whiteboardId: 'temp', // Will be set by parent component
      type: canvasState.tool.type,
      x: point.x,
      y: point.y,
      color: canvasState.tool.color,
      strokeWidth: canvasState.tool.strokeWidth,
      fill: canvasState.tool.fill,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      userId: 'temp' // Will be set by parent component
    }

    switch (canvasState.tool.type) {
      case 'pen':
        currentElement.value = {
          ...baseElement,
          points: [point]
        } as DrawingElement
        break
        
      case 'line':
        currentElement.value = {
          ...baseElement,
          endX: point.x,
          endY: point.y
        } as DrawingElement
        break
        
      case 'rectangle':
      case 'circle':
        currentElement.value = {
          ...baseElement,
          width: 0,
          height: 0
        } as DrawingElement
        break
        
      case 'text':
        // Text tool will be handled separately
        break
    }
  }

  const continueDrawing = (point: Point) => {
    if (!canvasState.isDrawing || !currentElement.value || !ctx.value) return

    switch (canvasState.tool.type) {
      case 'pen':
        if (currentElement.value.points) {
          currentElement.value.points.push(point)
        }
        break
        
      case 'line':
        currentElement.value.endX = point.x
        currentElement.value.endY = point.y
        break
        
      case 'rectangle':
        currentElement.value.width = point.x - currentElement.value.x
        currentElement.value.height = point.y - currentElement.value.y
        break
        
      case 'circle':
        const radius = Math.sqrt(
          Math.pow(point.x - currentElement.value.x, 2) + 
          Math.pow(point.y - currentElement.value.y, 2)
        )
        currentElement.value.width = radius * 2
        currentElement.value.height = radius * 2
        break
    }

    redrawCanvas()
  }

  const endDrawing = () => {
    if (!canvasState.isDrawing || !currentElement.value) return

    canvasState.isDrawing = false
    
    // Add element to elements array
    canvasState.elements.push(currentElement.value)
    
    // Add to history for undo/redo
    const newHistory = canvasState.history.slice(0, canvasState.currentHistoryIndex + 1)
    newHistory.push([...canvasState.elements])
    canvasState.history = newHistory
    canvasState.currentHistoryIndex = newHistory.length - 1

    currentElement.value = null
    
    // Emit drawing event
    emitDrawingEvent({
      type: 'end',
      point: { x: 0, y: 0 },
      tool: canvasState.tool,
      element: canvasState.elements[canvasState.elements.length - 1]
    })
  }

  const drawElement = (element: DrawingElement) => {
    if (!ctx.value) return

    ctx.value.strokeStyle = element.color
    ctx.value.lineWidth = element.strokeWidth || 2
    ctx.value.fillStyle = element.fill || 'transparent'

    switch (element.type) {
      case 'pen':
        if (element.points && element.points.length > 1) {
          ctx.value.beginPath()
          ctx.value.moveTo(element.points[0].x, element.points[0].y)
          
          for (let i = 1; i < element.points.length; i++) {
            ctx.value.lineTo(element.points[i].x, element.points[i].y)
          }
          
          ctx.value.stroke()
        }
        break
        
      case 'line':
        ctx.value.beginPath()
        ctx.value.moveTo(element.x, element.y)
        ctx.value.lineTo(element.endX || element.x, element.endY || element.y)
        ctx.value.stroke()
        break
        
      case 'rectangle':
        if (element.width && element.height) {
          ctx.value.beginPath()
          ctx.value.rect(element.x, element.y, element.width, element.height)
          
          if (element.fill && element.fill !== 'transparent') {
            ctx.value.fill()
          }
          ctx.value.stroke()
        }
        break
        
      case 'circle':
        if (element.width && element.height) {
          const radius = Math.min(element.width, element.height) / 2
          ctx.value.beginPath()
          ctx.value.arc(
            element.x + element.width / 2, 
            element.y + element.height / 2, 
            radius, 
            0, 
            2 * Math.PI
          )
          
          if (element.fill && element.fill !== 'transparent') {
            ctx.value.fill()
          }
          ctx.value.stroke()
        }
        break
        
      case 'text':
        if (element.text) {
          ctx.value.font = `${element.fontSize || 16}px ${element.fontFamily || 'Arial'}`
          ctx.value.fillStyle = element.color
          ctx.value.fillText(element.text, element.x, element.y)
        }
        break
    }
  }

  const redrawCanvas = () => {
    if (!ctx.value || !canvasRef.value) return

    // Clear canvas
    ctx.value.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)

    // Draw all elements
    canvasState.elements.forEach(drawElement)

    // Draw current element being drawn
    if (currentElement.value) {
      drawElement(currentElement.value)
    }
  }

  const clearCanvas = () => {
    canvasState.elements = []
    canvasState.history = [[]]
    canvasState.currentHistoryIndex = 0
    redrawCanvas()
  }

  const undo = () => {
    if (canvasState.currentHistoryIndex > 0) {
      canvasState.currentHistoryIndex--
      canvasState.elements = [...canvasState.history[canvasState.currentHistoryIndex]]
      redrawCanvas()
    }
  }

  const redo = () => {
    if (canvasState.currentHistoryIndex < canvasState.history.length - 1) {
      canvasState.currentHistoryIndex++
      canvasState.elements = [...canvasState.history[canvasState.currentHistoryIndex]]
      redrawCanvas()
    }
  }

  const setTool = (tool: Partial<DrawingTool>) => {
    Object.assign(canvasState.tool, tool)
  }

  const loadElements = (elements: DrawingElement[]) => {
    canvasState.elements = elements
    canvasState.history = [elements]
    canvasState.currentHistoryIndex = 0
    redrawCanvas()
  }

  // Event handlers
  const handleMouseDown = (e: MouseEvent) => {
    e.preventDefault()
    const point = getMousePos(e)
    startDrawing(point)
  }

  const handleMouseMove = (e: MouseEvent) => {
    e.preventDefault()
    const point = getMousePos(e)
    continueDrawing(point)
  }

  const handleMouseUp = (e: MouseEvent) => {
    e.preventDefault()
    endDrawing()
  }

  const handleTouchStart = (e: TouchEvent) => {
    e.preventDefault()
    const point = getTouchPos(e)
    startDrawing(point)
  }

  const handleTouchMove = (e: TouchEvent) => {
    e.preventDefault()
    const point = getTouchPos(e)
    continueDrawing(point)
  }

  const handleTouchEnd = (e: TouchEvent) => {
    e.preventDefault()
    endDrawing()
  }

  // Drawing event emission (for WebSocket)
  const drawingEventCallbacks = ref<Array<(event: DrawingEvent) => void>>([])
  
  const onDrawingEvent = (callback: (event: DrawingEvent) => void) => {
    drawingEventCallbacks.value.push(callback)
  }

  const emitDrawingEvent = (event: DrawingEvent) => {
    drawingEventCallbacks.value.forEach(callback => callback(event))
  }

  // Setup canvas event listeners
  const setupCanvas = () => {
    if (!canvasRef.value) return

    // Mouse events
    canvasRef.value.addEventListener('mousedown', handleMouseDown)
    canvasRef.value.addEventListener('mousemove', handleMouseMove)
    canvasRef.value.addEventListener('mouseup', handleMouseUp)
    canvasRef.value.addEventListener('mouseleave', handleMouseUp)

    // Touch events
    canvasRef.value.addEventListener('touchstart', handleTouchStart)
    canvasRef.value.addEventListener('touchmove', handleTouchMove)
    canvasRef.value.addEventListener('touchend', handleTouchEnd)
  }

  const cleanupCanvas = () => {
    if (!canvasRef.value) return

    // Remove mouse events
    canvasRef.value.removeEventListener('mousedown', handleMouseDown)
    canvasRef.value.removeEventListener('mousemove', handleMouseMove)
    canvasRef.value.removeEventListener('mouseup', handleMouseUp)
    canvasRef.value.removeEventListener('mouseleave', handleMouseUp)

    // Remove touch events
    canvasRef.value.removeEventListener('touchstart', handleTouchStart)
    canvasRef.value.removeEventListener('touchmove', handleTouchMove)
    canvasRef.value.removeEventListener('touchend', handleTouchEnd)
  }

  return {
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
    // Computed properties
    canUndo: computed(() => canvasState.currentHistoryIndex > 0),
    canRedo: computed(() => canvasState.currentHistoryIndex < canvasState.history.length - 1)
  }
}