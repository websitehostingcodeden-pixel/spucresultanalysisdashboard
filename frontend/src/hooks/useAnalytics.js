/**
 * useAnalytics Hook
 * 
 * Fetches analytics data and caches result
 * Prevents duplicate API calls
 */

import { useEffect, useCallback } from 'react'
import { useStore } from '../store/store'
import { analyticsService } from '../services/analyticsService'

export const useAnalytics = (uploadId) => {
  const { analytics, setIsLoading, setErrorMessage, clearError, updateAnalytics } = useStore()

  // Fetch analytics on mount or when uploadId changes
  useEffect(() => {
    if (!uploadId) {
      setErrorMessage('No upload ID provided')
      return
    }

    // Return early if already cached
    if (analytics && analytics.upload_id === uploadId) {
      return
    }

    const fetchAnalytics = async () => {
      setIsLoading(true)
      clearError()

      const result = await analyticsService.getAnalytics(uploadId)
      
      if (result.success) {
        updateAnalytics(result.data)
        clearError()
      } else {
        setErrorMessage(result.error || 'Failed to fetch analytics')
      }

      setIsLoading(false)
    }

    fetchAnalytics()
  }, [uploadId])

  return {
    analytics: analytics?.analytics,
    loading: false, // Use store loading state if needed
    error: null,
  }
}

export default useAnalytics
