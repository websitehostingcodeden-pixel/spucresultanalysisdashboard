/**
 * Upload Service
 * 
 * Handles file uploads to backend
 */

import { api } from '../api/client'

export const uploadService = {
  /**
   * Upload Excel file
   * 
   * @param {File} file - Excel file to upload
   * @returns {Promise} Response with upload_id and quality report
   */
  uploadFile: async (file) => {
    try {
      const response = await api.upload(file)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Upload failed'
      }
    }
  },

  /**
   * Validate file before upload
   */
  validateFile: (file) => {
    const maxSize = 5 * 1024 * 1024 // 5MB
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel'
    ]

    if (!file) {
      return { valid: false, error: 'No file selected' }
    }

    if (file.size > maxSize) {
      return { valid: false, error: 'File size exceeds 5MB limit' }
    }

    if (!allowedTypes.includes(file.type)) {
      return { valid: false, error: 'Only Excel files (.xlsx, .xls) are allowed' }
    }

    return { valid: true }
  }
}

export default uploadService
