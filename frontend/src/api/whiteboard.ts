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

  return {
    type: element.type,
    x: element.x,
    y: element.y,
    width: element.width && element.width >= 0 ? element.width : null,
    height: element.height && element.height >= 0 ? element.height : null,
    end_x: element.endX,
    end_y: element.endY,
    // Convert points format: {x, y} objects to {x: float, y: float} dictionary
    points: element.points ? element.points.map(point => ({ x: point.x, y: point.y })) : null,
    color: ensureHexColor(element.color),
    // Ensure stroke_width is integer if provided
    stroke_width: element.strokeWidth ? Math.max(1, Math.min(100, Math.round(element.strokeWidth))) : null,
    fill_color: element.fill ? ensureHexColor(element.fill) : null,
    text_content: element.text ? element.text.substring(0, 1000) : null,
    font_size: element.fontSize ? Math.max(8, Math.min(72, Math.round(element.fontSize))) : null,
    font_family: element.fontFamily ? element.fontFamily.substring(0, 100) : null
  }
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