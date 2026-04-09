/**
 * Auth Context & Hook
 * 
 * Manages authentication state with JWT tokens and refresh logic
 */

import React, { createContext, useContext, useState, useCallback } from 'react'

const AuthContext = createContext(null)

const TOKEN_KEY = import.meta.env.VITE_AUTH_TOKEN_KEY || 'aris_auth_token'
const REFRESH_TOKEN_KEY = import.meta.env.VITE_REFRESH_TOKEN_KEY || 'aris_refresh_token'

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    return !!token
  })

  const [user, setUser] = useState(() => {
    const userData = localStorage.getItem('aris_user')
    return userData ? JSON.parse(userData) : null
  })

  // Store both access and refresh tokens
  const login = useCallback((username, password, accessToken, refreshToken) => {
    localStorage.setItem(TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    localStorage.setItem('aris_user', JSON.stringify({ username }))
    setIsAuthenticated(true)
    setUser({ username })
    return Promise.resolve()
  }, [])

  // Force logout - clear all tokens
  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem('aris_user')
    setIsAuthenticated(false)
    setUser(null)
    window.location.href = '/login'
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
