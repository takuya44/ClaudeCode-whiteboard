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
const convertElementToBackend = (element: Omit<DrawingElement, 'id' | 'createdAt' | 'updatedAt' | 'whiteboardId' | 'userId'>): any => {
  return {
    type: element.type,
    x: element.x,
    y: element.y,
    width: element.width,
    height: element.height,
    end_x: element.endX,
    end_y: element.endY,
    points: element.points,
    color: element.color,
    stroke_width: element.strokeWidth,
    fill_color: element.fill,
    text_content: element.text,
    font_size: element.fontSize,
    font_family: element.fontFamily
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
    const elementsForBackend = elements.map(element => convertElementToBackend({
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