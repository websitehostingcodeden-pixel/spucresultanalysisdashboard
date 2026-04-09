/**
 * Auth Context & Hook
 * 
 * Manages authentication state
 */

import React, { createContext, useContext, useState, useCallback } from 'react'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // Check if token exists in localStorage
    const token = localStorage.getItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'aris_auth_token')
    return !!token
  })

  const [user, setUser] = useState(() => {
    const userData = localStorage.getItem('aris_user')
    return userData ? JSON.parse(userData) : null
  })

  // Simple login (in real app, would validate with backend)
  const login = useCallback((username, password) => {
    // For demo, accept any credentials
    // In production, this would call backend auth endpoint
    const token = `token_${Date.now()}`
    localStorage.setItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'aris_auth_token', token)
    localStorage.setItem('aris_user', JSON.stringify({ username }))
    setIsAuthenticated(true)
    setUser({ username })
    return Promise.resolve()
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'aris_auth_token')
    localStorage.removeItem('aris_user')
    setIsAuthenticated(false)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
