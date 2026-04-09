/**
 * CENTRALIZED API CLIENT
 * 
 * All API calls MUST go through this client.
 * - Configures base URL from environment
 * - Handles authentication tokens
 * - Implements global error handling
 * - Provides typed API methods
 */

import axios from 'axios'

const API_BASE_URL = '/api'
const TOKEN_KEY = import.meta.env.VITE_AUTH_TOKEN_KEY || 'aris_auth_token'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,  // Increased to 30 seconds for analytics computation
  headers: {
    'Content-Type': 'application/json',
  }
})

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Global error handler
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      window.location.href = '/login'
    }
    
    // Build detailed error object
    const errorData = {
      status: error.response?.status || error.code || 'UNKNOWN',
      message: error.response?.data?.message || error.message || 'Unknown error',
      code: error.response?.data?.code || 'UNKNOWN_ERROR',
      url: error.config?.url || 'unknown',
      method: error.config?.method || 'unknown'
    }
    
    // Log with proper formatting so details are visible in console
    console.error('API Error:', errorData.status, errorData.message, errorData)
    console.error('Full error details:', {
      responseStatus: error.response?.status,
      responseData: error.response?.data,
      message: error.message,
      url: error.config?.url
    })
    
    return Promise.reject(errorData)
  }
)

/**
 * API Methods
 */
export const api = {
  // ===== UPLOAD =====
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000  // 60 second timeout for file uploads
    })
  },

  // ===== ANALYTICS =====
  getAnalytics: (uploadId) => 
    apiClient.get(`/analytics/${uploadId}/`),

  getToppers: (uploadId) => 
    apiClient.get(`/toppers/${uploadId}/`),

  getSectionToppers: (uploadId) => 
    apiClient.get(`/toppers/section/${uploadId}/`),

  getSections: (uploadId) => 
    apiClient.get(`/sections/${uploadId}/`),

  getSubjects: (uploadId) => 
    apiClient.get(`/subjects/${uploadId}/`),

  // ===== EXPORT =====
  exportExcel: (uploadId) => 
    apiClient.get(`/export/excel/${uploadId}/`, {
      responseType: 'blob'
    }),

  // ===== LEGACY =====
  getGlobalAnalytics: () => 
    apiClient.get('/analytics/'),

  getStreamAnalytics: (stream) => 
    apiClient.get('/analytics/stream/', { params: { stream } }),

  getSectionAnalytics: (section) => 
    apiClient.get('/analytics/section/', { params: { section } }),

  getUploadHistory: () => 
    apiClient.get('/uploads/'),

  getStats: () => 
    apiClient.get('/stats/'),
}

export default apiClient
