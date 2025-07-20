import { apiRequest } from './index'
import type { Whiteboard, DrawingElement, User, ApiResponse, PaginatedResponse } from '@/types'

export interface CreateWhiteboardRequest {
  title: string
  description?: string
  isPublic: boolean
}

export interface UpdateWhiteboardRequest {
  title?: string
  description?: string
  isPublic?: boolean
}

// Schema conversion utilities
const ensureHexColor = (color: string): string => {
  if (!color) return '#000000'
  if (color.startsWith('#') && color.length === 7) return color
  if (color.startsWith('#') && color.length === 4) {
    // Convert #RGB to #RRGGBB
    return '#' + color[1] + color[1] + color[2] + color[2] + color[3] + color[3]
  }
  return '#000000' // Default to black if invalid format
}

const convertElementToBackend = (element: Omit<DrawingElement, 'id' | 'createdAt' | 'updatedAt' | 'whiteboardId' | 'userId'>): any => {
  // Filter out unsupported types for backend
  const supportedTypes = ['pen', 'line', 'rectangle', 'circle', 'text', 'sticky']
  if (!supportedTypes.includes(element.type)) {
    return null // Skip unsupported types like 'eraser' and 'select'
  }

  // Ensure required fields are valid
  if (typeof element.x !== 'number' || typeof element.y !== 'number') {
    console.warn('Invalid coordinates for element:', element)
    return null
  }

  if (!element.color) {
    console.warn('Missing color for element:', element)
    return null
  }

  const converted = {
    type: element.type,
    x: Number(element.x),
    y: Number(element.y),
    width: element.width && element.width >= 0 ? Number(element.width) : undefined,
    height: element.height && element.height >= 0 ? Number(element.height) : undefined,
    end_x: element.endX !== undefined ? Number(element.endX) : undefined,
    end_y: element.endY !== undefined ? Number(element.endY) : undefined,
    // Convert points format: {x, y} objects to {x: float, y: float} dictionary
    points: element.points && element.points.length > 0 
      ? element.points.map(point => ({ x: Number(point.x), y: Number(point.y) })) 
      : undefined,
    color: ensureHexColor(element.color),
    // Ensure stroke_width is integer if provided
    stroke_width: element.strokeWidth ? Math.max(1, Math.min(100, Math.round(Number(element.strokeWidth)))) : undefined,
    fill_color: element.fill ? ensureHexColor(element.fill) : undefined,
    text_content: element.text ? String(element.text).substring(0, 1000) : undefined,
    font_size: element.fontSize ? Math.max(8, Math.min(72, Math.round(Number(element.fontSize)))) : undefined,
    font_family: element.fontFamily ? String(element.fontFamily).substring(0, 100) : undefined
  }

  // Remove undefined values to avoid sending null fields
  Object.keys(converted).forEach(key => {
    if (converted[key as keyof typeof converted] === undefined) {
      delete converted[key as keyof typeof converted]
    }
  })

  return converted
}

export const whiteboardApi = {
  getWhiteboards(page = 1, perPage = 10): Promise<ApiResponse<PaginatedResponse<Whiteboard>>> {
    return apiRequest.get(`/whiteboards?page=${page}&per_page=${perPage}`)
  },

  getWhiteboard(id: string): Promise<ApiResponse<Whiteboard>> {
    return apiRequest.get(`/whiteboards/${id}`)
  },

  createWhiteboard(data: CreateWhiteboardRequest): Promise<ApiResponse<Whiteboard>> {
    return apiRequest.post('/whiteboards', data)
  },

  updateWhiteboard(id: string, data: UpdateWhiteboardRequest): Promise<ApiResponse<Whiteboard>> {
    return apiRequest.put(`/whiteboards/${id}`, data)
  },

  deleteWhiteboard(id: string): Promise<ApiResponse> {
    return apiRequest.delete(`/whiteboards/${id}`)
  },

  getWhiteboardElements(whiteboardId: string): Promise<ApiResponse<DrawingElement[]>> {
    return apiRequest.get(`/whiteboards/${whiteboardId}/elements`)
  },

  createElement(whiteboardId: string, element: Omit<DrawingElement, 'id' | 'createdAt' | 'updatedAt' | 'whiteboardId'>): Promise<ApiResponse<DrawingElement>> {
    return apiRequest.post(`/whiteboards/${whiteboardId}/elements`, element)
  },

  updateElement(whiteboardId: string, elementId: string, data: Partial<DrawingElement>): Promise<ApiResponse<DrawingElement>> {
    return apiRequest.put(`/whiteboards/${whiteboardId}/elements/${elementId}`, data)
  },

  deleteElement(whiteboardId: string, elementId: string): Promise<ApiResponse> {
    return apiRequest.delete(`/whiteboards/${whiteboardId}/elements/${elementId}`)
  },

  clearWhiteboard(whiteboardId: string): Promise<ApiResponse> {
    return apiRequest.delete(`/whiteboards/${whiteboardId}/elements`)
  },

  saveElements(whiteboardId: string, elements: DrawingElement[]): Promise<ApiResponse<DrawingElement[]>> {
    // Convert elements to backend schema format and exclude server-managed fields
    const elementsForBackend = elements
      .map(element => convertElementToBackend({
        type: element.type,
        x: element.x,
        y: element.y,
        width: element.width,
        height: element.height,
        endX: element.endX,
        endY: element.endY,
        points: element.points,
        color: element.color,
        strokeWidth: element.strokeWidth,
        fill: element.fill,
        text: element.text,
        fontSize: element.fontSize,
        fontFamily: element.fontFamily
      }))
      .filter(element => element !== null) // Remove unsupported elements
    
    console.log('API Request:', {
      endpoint: `/whiteboards/${whiteboardId}/elements/batch`,
      originalElements: elements.length,
      convertedElements: elementsForBackend.length,
      payload: { elements: elementsForBackend }
    })
    
    // 詳細な要素内容をログ出力
    elementsForBackend.forEach((element, index) => {
      console.log(`Element ${index}:`, element)
    })
    
    return apiRequest.put(`/whiteboards/${whiteboardId}/elements/batch`, {
      elements: elementsForBackend
    })
  },

  shareWhiteboard(whiteboardId: string, userEmails: string[]): Promise<ApiResponse> {
    return apiRequest.post(`/whiteboards/${whiteboardId}/share`, { userEmails })
  },

  getCollaborators(whiteboardId: string): Promise<ApiResponse<User[]>> {
    return apiRequest.get(`/whiteboards/${whiteboardId}/collaborators`)
  },

  removeCollaborator(whiteboardId: string, userId: string): Promise<ApiResponse> {
    return apiRequest.delete(`/whiteboards/${whiteboardId}/collaborators/${userId}`)
  },
}