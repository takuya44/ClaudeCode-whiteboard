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
  type: 'pen' | 'rectangle' | 'circle' | 'text' | 'sticky'
  x: number
  y: number
  width?: number
  height?: number
  color: string
  strokeWidth?: number
  text?: string
  createdAt: string
  updatedAt: string
  userId: string
}

export interface WebSocketMessage {
  type: 'draw' | 'erase' | 'cursor' | 'user_join' | 'user_leave'
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