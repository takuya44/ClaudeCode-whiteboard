export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  role: 'admin' | 'user'
  createdAt: string
  updatedAt: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface Whiteboard {
  id: string
  title: string
  description?: string
  ownerId: string
  isPublic: boolean
  createdAt: string
  updatedAt: string
  collaborators: User[]
}

export interface DrawingElement {
  id: string
  whiteboardId: string
  type: 'pen' | 'line' | 'rectangle' | 'circle' | 'text' | 'sticky' | 'eraser' | 'select'
  x: number
  y: number
  width?: number
  height?: number
  endX?: number
  endY?: number
  points?: Array<{x: number, y: number}>
  color: string
  strokeWidth?: number
  fill?: string
  text?: string
  fontSize?: number
  fontFamily?: string
  createdAt: string
  updatedAt: string
  userId: string
}

export interface DrawingTool {
  type: 'pen' | 'line' | 'rectangle' | 'circle' | 'text' | 'eraser' | 'select'
  color: string
  strokeWidth: number
  fill?: string
  fontSize?: number
}

export interface Point {
  x: number
  y: number
}

export interface CanvasState {
  isDrawing: boolean
  tool: DrawingTool
  elements: DrawingElement[]
  history: DrawingElement[][]
  currentHistoryIndex: number
}

export interface DrawingEvent {
  type: 'start' | 'move' | 'end'
  point: Point
  tool: DrawingTool
  element?: DrawingElement
}

export interface WebSocketMessage {
  type: 'draw' | 'erase' | 'cursor' | 'user_join' | 'user_leave' | 'ping' | 'pong' | 'drawing_event'
  data: any
  userId: string
  timestamp: string
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T = any> {
  data: T[]
  meta: {
    total: number
    page: number
    perPage: number
    totalPages: number
  }
}