import { ref, reactive, onUnmounted } from 'vue'
import type { WebSocketMessage, DrawingElement, DrawingEvent } from '@/types'

interface WebSocketState {
  isConnected: boolean
  isConnecting: boolean
  reconnectAttempts: number
  lastError: string | null
}

interface WebSocketConfig {
  url: string
  reconnectInterval: number
  maxReconnectAttempts: number
  heartbeatInterval: number
}

export function useWebSocket(config: Partial<WebSocketConfig> = {}) {
  const defaultConfig: WebSocketConfig = {
    url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
    heartbeatInterval: 30000
  }

  const wsConfig = { ...defaultConfig, ...config }

  const socket = ref<WebSocket | null>(null)
  const state = reactive<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    reconnectAttempts: 0,
    lastError: null
  })

  // Message handlers
  const messageHandlers = ref<Map<string, Array<(data: any) => void>>>(new Map())
  
  // Reconnection timer
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null

  const connect = (whiteboardId: string, userId: string) => {
    if (state.isConnected || state.isConnecting) {
      return Promise.resolve()
    }

    return new Promise<void>((resolve, reject) => {
      try {
        state.isConnecting = true
        state.lastError = null

        const wsUrl = `${wsConfig.url}/${whiteboardId}?userId=${userId}`
        socket.value = new WebSocket(wsUrl)

        socket.value.onopen = () => {
          state.isConnected = true
          state.isConnecting = false
          state.reconnectAttempts = 0
          
          // Start heartbeat
          startHeartbeat()
          
          console.log('WebSocket connected successfully')
          resolve()
        }

        socket.value.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        socket.value.onclose = (event) => {
          state.isConnected = false
          state.isConnecting = false
          
          // Stop heartbeat
          stopHeartbeat()
          
          if (event.code !== 1000) { // Not a normal closure
            console.log('WebSocket connection closed unexpectedly:', event.code, event.reason)
            scheduleReconnect(whiteboardId, userId)
          } else {
            console.log('WebSocket connection closed normally')
          }
        }

        socket.value.onerror = (error) => {
          state.lastError = 'WebSocket connection error'
          state.isConnecting = false
          console.error('WebSocket error:', error)
          reject(new Error('WebSocket connection failed'))
        }

      } catch (error) {
        state.isConnecting = false
        state.lastError = 'Failed to create WebSocket connection'
        reject(error)
      }
    })
  }

  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    
    stopHeartbeat()
    
    if (socket.value) {
      socket.value.close(1000, 'User disconnected')
      socket.value = null
    }
    
    state.isConnected = false
    state.isConnecting = false
    state.reconnectAttempts = 0
  }

  const scheduleReconnect = (whiteboardId: string, userId: string) => {
    if (state.reconnectAttempts >= wsConfig.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      state.lastError = 'Connection failed after multiple attempts'
      return
    }

    state.reconnectAttempts++
    console.log(`Attempting to reconnect (${state.reconnectAttempts}/${wsConfig.maxReconnectAttempts})...`)

    reconnectTimer = setTimeout(() => {
      connect(whiteboardId, userId).catch((error) => {
        console.error('Reconnection failed:', error)
      })
    }, wsConfig.reconnectInterval)
  }

  const startHeartbeat = () => {
    heartbeatTimer = setInterval(() => {
      if (state.isConnected && socket.value) {
        sendMessage({
          type: 'ping',
          data: {},
          userId: '',
          timestamp: new Date().toISOString()
        })
      }
    }, wsConfig.heartbeatInterval)
  }

  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  const sendMessage = (message: WebSocketMessage) => {
    if (!state.isConnected || !socket.value) {
      console.warn('WebSocket not connected, message not sent:', message)
      return false
    }

    try {
      socket.value.send(JSON.stringify(message))
      return true
    } catch (error) {
      console.error('Failed to send WebSocket message:', error)
      return false
    }
  }

  const handleMessage = (message: WebSocketMessage) => {
    const handlers = messageHandlers.value.get(message.type) || []
    handlers.forEach(handler => {
      try {
        handler(message.data)
      } catch (error) {
        console.error(`Error in message handler for type ${message.type}:`, error)
      }
    })
  }

  const onMessage = (type: string, handler: (data: any) => void) => {
    if (!messageHandlers.value.has(type)) {
      messageHandlers.value.set(type, [])
    }
    messageHandlers.value.get(type)!.push(handler)

    // Return unsubscribe function
    return () => {
      const handlers = messageHandlers.value.get(type)
      if (handlers) {
        const index = handlers.indexOf(handler)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    }
  }

  const offMessage = (type: string, handler: (data: any) => void) => {
    const handlers = messageHandlers.value.get(type)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  // Drawing-specific methods
  const sendDrawingUpdate = (element: DrawingElement, userId: string) => {
    return sendMessage({
      type: 'draw',
      data: { element },
      userId,
      timestamp: new Date().toISOString()
    })
  }

  const sendDrawingEvent = (event: DrawingEvent, userId: string) => {
    return sendMessage({
      type: 'drawing_event',
      data: event,
      userId,
      timestamp: new Date().toISOString()
    })
  }

  const sendCursorUpdate = (x: number, y: number, userId: string) => {
    return sendMessage({
      type: 'cursor',
      data: { x, y },
      userId,
      timestamp: new Date().toISOString()
    })
  }

  const sendUserJoin = (userId: string, userName: string) => {
    return sendMessage({
      type: 'user_join',
      data: { userId, userName },
      userId,
      timestamp: new Date().toISOString()
    })
  }

  const sendUserLeave = (userId: string) => {
    return sendMessage({
      type: 'user_leave',
      data: { userId },
      userId,
      timestamp: new Date().toISOString()
    })
  }

  // Cleanup on component unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    // State
    state,
    isConnected: () => state.isConnected,
    isConnecting: () => state.isConnecting,
    lastError: () => state.lastError,
    
    // Connection methods
    connect,
    disconnect,
    
    // Message methods
    sendMessage,
    onMessage,
    offMessage,
    
    // Drawing-specific methods
    sendDrawingUpdate,
    sendDrawingEvent,
    sendCursorUpdate,
    sendUserJoin,
    sendUserLeave
  }
}