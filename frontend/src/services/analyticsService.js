/**
 * Analytics Service
 * 
 * Handles fetching analytics data from backend
 */

import { api } from '../api/client'

export const analyticsService = {
  /**
   * Fetch complete analytics for an upload
   */
  getAnalytics: async (uploadId) => {
    try {
      const response = await api.getAnalytics(uploadId)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to fetch analytics'
      }
    }
  },

  /**
   * Fetch toppers list (college, science, commerce)
   */
  getToppers: async (uploadId) => {
    try {
      const response = await api.getToppers(uploadId)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to fetch toppers'
      }
    }
  },

  /**
   * Fetch section-wise toppers
   */
  getSectionToppers: async (uploadId) => {
    try {
      const response = await api.getSectionToppers(uploadId)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to fetch section toppers'
      }
    }
  },

  /**
   * Fetch section performance
   */
  getSections: async (uploadId) => {
    try {
      const response = await api.getSections(uploadId)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to fetch sections'
      }
    }
  },

  /**
   * Fetch subject analysis
   */
  getSubjects: async (uploadId) => {
    try {
      const response = await api.getSubjects(uploadId)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to fetch subjects'
      }
    }
  },

  /**
   * Download analytics as Excel
   */
  downloadExcel: async (uploadId) => {
    try {
      const response = await api.exportExcel(uploadId)
      
      // Create blob and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `ARIS_Analytics_${uploadId}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      }
    }
  }
}

export default analyticsService
