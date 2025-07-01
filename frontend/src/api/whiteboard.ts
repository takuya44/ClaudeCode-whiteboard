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