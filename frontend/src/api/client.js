/**
 * CENTRALIZED API CLIENT
 * 
 * All API calls MUST go through this client.
 * - Configures base URL from environment
 * - Handles authentication tokens
 * - Implements JWT refresh token flow
 * - Provides typed API methods
 */

import axios from 'axios'

// Get API base URL from environment, default to /api for dev (proxy)
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'
const TOKEN_KEY = import.meta.env.VITE_AUTH_TOKEN_KEY || 'aris_auth_token'
const REFRESH_TOKEN_KEY = import.meta.env.VITE_REFRESH_TOKEN_KEY || 'aris_refresh_token'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Request interceptor: Attach token
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

// Response interceptor: Handle 401 with refresh token
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const originalRequest = error.config

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return apiClient(originalRequest)
          })
          .catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      // Try to refresh token
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

      if (!refreshToken) {
        // No refresh token - force logout
        forceLogout()
        return Promise.reject(error)
      }

      return apiClient
        .post('/token/refresh/', { refresh: refreshToken })
        .then(res => {
          const { access } = res.data
          localStorage.setItem(TOKEN_KEY, access)
          apiClient.defaults.headers.common.Authorization = `Bearer ${access}`
          originalRequest.headers.Authorization = `Bearer ${access}`
          processQueue(null, access)
          return apiClient(originalRequest)
        })
        .catch(err => {
          // Refresh failed - logout
          forceLogout()
          processQueue(err, null)
          return Promise.reject(err)
        })
        .finally(() => {
          isRefreshing = false
        })
    }
    
    // Build detailed error object
    const errorData = {
      status: error.response?.status || error.code || 'UNKNOWN',
      message: error.response?.data?.message || error.message || 'Unknown error',
      code: error.response?.data?.code || 'UNKNOWN_ERROR',
      url: error.config?.url || 'unknown',
      method: error.config?.method || 'unknown'
    }
    
    console.error('API Error:', errorData.status, errorData.message)
    return Promise.reject(errorData)
  }
)

// Force logout helper
function forceLogout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem('aris_user')
  window.location.href = '/login'
}

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

  // ===== AUTHENTICATION =====
  login: (username, password) =>
    apiClient.post('/login/', { username, password }),

  refreshToken: (refresh) =>
    apiClient.post('/token/refresh/', { refresh }),

  logout: () =>
    apiClient.post('/logout/'),
}

export default apiClient
