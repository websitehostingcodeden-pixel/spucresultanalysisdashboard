/**
 * Global State Store
 * 
 * Manages:
 * - uploadId (current upload)
 * - analytics data (cached)
 * - loading state
 * - error state
 * - presentation mode toggle
 */

import React, { createContext, useContext, useState, useCallback } from 'react'

const StoreContext = createContext(null)

export const StoreProvider = ({ children }) => {
  const [uploadId, setUploadId] = useState(() => {
    return localStorage.getItem(import.meta.env.VITE_UPLOAD_ID_KEY || 'aris_upload_id')
  })

  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [presentationMode, setPresentationMode] = useState(false)

  // Store upload ID persistently
  const updateUploadId = useCallback((id) => {
    setUploadId(id)
    if (id) {
      localStorage.setItem(import.meta.env.VITE_UPLOAD_ID_KEY || 'aris_upload_id', id)
    } else {
      localStorage.removeItem(import.meta.env.VITE_UPLOAD_ID_KEY || 'aris_upload_id')
    }
  }, [])

  // Update analytics
  const updateAnalytics = useCallback((data) => {
    setAnalytics(data)
  }, [])

  // Set loading state
  const setIsLoading = useCallback((isLoading) => {
    setLoading(isLoading)
  }, [])

  // Set error
  const setErrorMessage = useCallback((message) => {
    setError(message)
  }, [])

  // Clear error
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  // Toggle presentation mode
  const togglePresentationMode = useCallback(() => {
    setPresentationMode(prev => !prev)
  }, [])

  // Reset store
  const reset = useCallback(() => {
    setUploadId(null)
    setAnalytics(null)
    setError(null)
    setLoading(false)
    localStorage.removeItem(import.meta.env.VITE_UPLOAD_ID_KEY || 'aris_upload_id')
  }, [])

  return (
    <StoreContext.Provider value={{
      uploadId,
      updateUploadId,
      analytics,
      updateAnalytics,
      loading,
      setIsLoading,
      error,
      setErrorMessage,
      clearError,
      presentationMode,
      togglePresentationMode,
      reset,
    }}>
      {children}
    </StoreContext.Provider>
  )
}

export const useStore = () => {
  const context = useContext(StoreContext)
  if (!context) {
    throw new Error('useStore must be used within StoreProvider')
  }
  return context
}
